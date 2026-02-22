"""
LiteLLM pricing integration service.

Uses LiteLLM's model_cost data to look up and sync model pricing.
LiteLLM maintains an up-to-date pricing database for 2500+ models across
all major providers.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.provider import ModelImplementation, ModelProvider

logger = logging.getLogger(__name__)

# Mapping from our provider names to LiteLLM provider prefixes.
# LiteLLM uses prefixes like "deepseek/", "dashscope/", "moonshot/" etc.
# OpenAI and Anthropic models typically have no prefix in LiteLLM.
PROVIDER_PREFIX_MAP = {
    "OpenAI": ["", "openai/"],
    "Anthropic": ["", "anthropic/"],
    "Google AI": ["", "gemini/", "vertex_ai/"],
    "DeepSeek": ["deepseek/", ""],
    "阿里云百炼": ["dashscope/"],
    "智谱AI": ["zai/", "zhipu/"],
    "Moonshot": ["moonshot/"],
    "硅基流动": ["openrouter/", ""],
    "Azure OpenAI": ["azure/"],
    "百度千帆": ["baidu/"],
    "讯飞星火": ["spark/"],
    "字节跳动": ["volcengine/"],
}


def _get_model_cost() -> dict:
    """Load LiteLLM's model_cost data (lazy import to avoid startup overhead)."""
    import litellm
    return litellm.model_cost


def _convert_per_token_to_per_1m(cost_per_token: float) -> float:
    """Convert LiteLLM's per-token cost to our per-1M-tokens format."""
    return cost_per_token * 1_000_000


def lookup_model_price(
    provider_model_id: str,
    provider_name: Optional[str] = None,
) -> Optional[Dict[str, float]]:
    """
    Look up a model's pricing from LiteLLM's model_cost database.

    Tries multiple matching strategies:
    1. Exact match with provider_model_id
    2. Match with provider prefix + provider_model_id
    3. Match with common aliases

    Args:
        provider_model_id: The model ID used by the provider (e.g. "gpt-4o", "deepseek-chat")
        provider_name: Optional provider name for prefix-based matching

    Returns:
        Dict with input_price and output_price (per 1M tokens) or None if not found
    """
    model_cost = _get_model_cost()

    # Strategy 1: Exact match
    if provider_model_id in model_cost:
        entry = model_cost[provider_model_id]
        return _extract_pricing(entry)

    # Strategy 2: Try with provider prefixes
    if provider_name:
        prefixes = PROVIDER_PREFIX_MAP.get(provider_name, [""])
        for prefix in prefixes:
            if not prefix:
                continue
            key = f"{prefix}{provider_model_id}"
            if key in model_cost:
                return _extract_pricing(model_cost[key])

    # Strategy 3: Try without version suffix (e.g. "claude-3-opus-20240229" -> "claude-3-opus")
    # Also try adding common suffixes
    variants = _generate_variants(provider_model_id, provider_name)
    for variant in variants:
        if variant in model_cost:
            return _extract_pricing(model_cost[variant])
        # Also try with provider prefixes
        if provider_name:
            prefixes = PROVIDER_PREFIX_MAP.get(provider_name, [""])
            for prefix in prefixes:
                if not prefix:
                    continue
                key = f"{prefix}{variant}"
                if key in model_cost:
                    return _extract_pricing(model_cost[key])

    # Strategy 4: Case-insensitive search
    lower_id = provider_model_id.lower()
    for key, entry in model_cost.items():
        if key.lower() == lower_id:
            return _extract_pricing(entry)
        # Also check if key ends with our model id (for prefixed entries)
        if key.lower().endswith(f"/{lower_id}"):
            return _extract_pricing(entry)

    return None


def _extract_pricing(entry: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """Extract and convert pricing from a LiteLLM model_cost entry."""
    input_cost = entry.get("input_cost_per_token")
    output_cost = entry.get("output_cost_per_token")

    if input_cost is None and output_cost is None:
        return None

    return {
        "input_price": _convert_per_token_to_per_1m(input_cost or 0),
        "output_price": _convert_per_token_to_per_1m(output_cost or 0),
    }


def _generate_variants(provider_model_id: str, provider_name: Optional[str] = None) -> List[str]:
    """Generate possible variant names for a model ID to improve matching."""
    variants = []

    # For Anthropic models with date suffixes like "claude-3-opus-20240229"
    # try the base name
    parts = provider_model_id.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 8:
        variants.append(parts[0])

    # For models with version like "gpt-4o-2024-11-20"
    # remove the date part
    if provider_model_id.count("-") >= 3:
        date_pattern_parts = provider_model_id.rsplit("-", 3)
        if len(date_pattern_parts) >= 4:
            try:
                year, month, day = date_pattern_parts[-3], date_pattern_parts[-2], date_pattern_parts[-1]
                if year.isdigit() and month.isdigit() and day.isdigit():
                    variants.append(date_pattern_parts[0] if len(date_pattern_parts) == 4
                                   else "-".join(date_pattern_parts[:-3]))
            except (ValueError, IndexError):
                pass

    # For Moonshot models, try the full path pattern
    if provider_model_id.startswith("moonshot-v1"):
        variants.append(f"moonshot/{provider_model_id}")

    return variants


def preview_sync(db: Session) -> List[Dict[str, Any]]:
    """
    Preview what prices would be updated by syncing from LiteLLM.

    Returns a list of changes that would be made, without actually updating.
    """
    results = []
    implementations = db.query(ModelImplementation).all()

    for impl in implementations:
        provider_name = impl.provider.name if impl.provider else None
        litellm_price = lookup_model_price(impl.provider_model_id, provider_name)

        current_pricing = impl.pricing_info or {}
        current_input = float(current_pricing.get("input_price", 0))
        current_output = float(current_pricing.get("output_price", 0))

        result = {
            "model_implementation_id": str(impl.id),
            "provider_model_id": impl.provider_model_id,
            "provider_name": provider_name,
            "model_name": impl.model.name if impl.model else None,
            "current_input_price": current_input,
            "current_output_price": current_output,
            "litellm_input_price": None,
            "litellm_output_price": None,
            "has_litellm_price": False,
            "price_changed": False,
        }

        if litellm_price:
            new_input = litellm_price["input_price"]
            new_output = litellm_price["output_price"]
            result["litellm_input_price"] = round(new_input, 6)
            result["litellm_output_price"] = round(new_output, 6)
            result["has_litellm_price"] = True
            result["price_changed"] = (
                abs(current_input - new_input) > 0.0001
                or abs(current_output - new_output) > 0.0001
            )

        results.append(result)

    return results


def sync_prices_from_litellm(
    db: Session,
    only_missing: bool = False,
    provider_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sync model prices from LiteLLM's model_cost database.

    Args:
        db: Database session
        only_missing: If True, only update models that have no pricing info
        provider_filter: Optional provider name to filter by

    Returns:
        Summary of sync results
    """
    query = db.query(ModelImplementation)

    if provider_filter:
        query = query.join(ModelProvider).filter(ModelProvider.name == provider_filter)

    implementations = query.all()

    updated = []
    skipped = []
    not_found = []

    for impl in implementations:
        provider_name = impl.provider.name if impl.provider else None

        # Skip if only_missing and already has pricing
        if only_missing and impl.pricing_info:
            current = impl.pricing_info
            if current.get("input_price") or current.get("output_price"):
                skipped.append({
                    "provider_model_id": impl.provider_model_id,
                    "provider": provider_name,
                    "reason": "already_has_pricing",
                })
                continue

        litellm_price = lookup_model_price(impl.provider_model_id, provider_name)

        if not litellm_price:
            not_found.append({
                "provider_model_id": impl.provider_model_id,
                "provider": provider_name,
            })
            continue

        # Update pricing info
        pricing_info = impl.pricing_info or {}
        old_input = float(pricing_info.get("input_price", 0))
        old_output = float(pricing_info.get("output_price", 0))

        new_input = round(litellm_price["input_price"], 6)
        new_output = round(litellm_price["output_price"], 6)

        pricing_info["input_price"] = new_input
        pricing_info["output_price"] = new_output
        pricing_info["last_updated"] = datetime.now(timezone.utc).isoformat()
        pricing_info["updated_by"] = "litellm"

        impl.pricing_info = pricing_info
        # Force SQLAlchemy to detect the JSONB change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(impl, "pricing_info")

        updated.append({
            "provider_model_id": impl.provider_model_id,
            "provider": provider_name,
            "old_input_price": old_input,
            "old_output_price": old_output,
            "new_input_price": new_input,
            "new_output_price": new_output,
        })

    db.commit()

    return {
        "updated_count": len(updated),
        "skipped_count": len(skipped),
        "not_found_count": len(not_found),
        "updated": updated,
        "skipped": skipped,
        "not_found": not_found,
    }


def get_litellm_price_for_model(provider_model_id: str, provider_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get full pricing details for a model from LiteLLM, including additional metadata.

    Returns pricing info plus context window and provider data from LiteLLM.
    """
    model_cost = _get_model_cost()

    # Reuse the lookup logic
    price = lookup_model_price(provider_model_id, provider_name)
    if not price:
        return None

    # Find the matching entry for additional metadata
    entry = None
    if provider_model_id in model_cost:
        entry = model_cost[provider_model_id]
    else:
        # Try with prefixes
        if provider_name:
            for prefix in PROVIDER_PREFIX_MAP.get(provider_name, [""]):
                key = f"{prefix}{provider_model_id}" if prefix else provider_model_id
                if key in model_cost:
                    entry = model_cost[key]
                    break

    result = {
        "input_price": price["input_price"],
        "output_price": price["output_price"],
    }

    if entry:
        result["max_tokens"] = entry.get("max_tokens")
        result["max_input_tokens"] = entry.get("max_input_tokens")
        result["litellm_provider"] = entry.get("litellm_provider")

    return result


# Reverse mapping: LiteLLM provider name -> our provider names
_LITELLM_PROVIDER_TO_OUR_PROVIDER = {
    "openai": ["OpenAI"],
    "anthropic": ["Anthropic"],
    "vertex_ai-language-models": ["Google AI"],
    "vertex_ai-chat-models": ["Google AI"],
    "gemini": ["Google AI"],
    "deepseek": ["DeepSeek"],
    "dashscope": ["阿里云百炼"],
    "zhipu": ["智谱AI"],
    "moonshot": ["Moonshot"],
    "azure": ["Azure OpenAI"],
    "azure_ai": ["Azure OpenAI"],
    "volcengine": ["字节跳动"],
}


def search_litellm_models(
    search: str = "",
    provider_name: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Search available models from LiteLLM's pricing database.

    Used by the frontend to populate autocomplete for model selection.

    Args:
        search: Search query to filter models by ID
        provider_name: Optional provider name to filter relevant models
        limit: Maximum number of results

    Returns:
        List of model entries with id, pricing, and metadata
    """
    model_cost = _get_model_cost()
    results = []

    # Determine which LiteLLM keys are relevant for this provider
    prefixes = None
    if provider_name:
        prefixes = PROVIDER_PREFIX_MAP.get(provider_name)

    search_lower = search.lower()

    for key, entry in model_cost.items():
        # Filter by provider if specified
        if prefixes is not None:
            matched = False
            for prefix in prefixes:
                if prefix == "":
                    # For empty prefix, check litellm_provider field
                    litellm_prov = entry.get("litellm_provider", "")
                    # Check if litellm_provider maps to our provider
                    our_providers = _LITELLM_PROVIDER_TO_OUR_PROVIDER.get(litellm_prov, [])
                    if provider_name in our_providers:
                        matched = True
                        break
                    # Also match if key has no "/" (top-level model, likely matching)
                    if "/" not in key and litellm_prov and provider_name in _LITELLM_PROVIDER_TO_OUR_PROVIDER.get(litellm_prov, []):
                        matched = True
                        break
                else:
                    if key.startswith(prefix):
                        matched = True
                        break
            if not matched:
                continue

        # Filter by search query
        if search_lower and search_lower not in key.lower():
            continue

        pricing = _extract_pricing(entry)
        if not pricing:
            continue

        # Extract the actual model ID (strip provider prefix for display)
        display_id = key
        if prefixes:
            for prefix in prefixes:
                if prefix and key.startswith(prefix):
                    display_id = key[len(prefix):]
                    break

        results.append({
            "litellm_key": key,
            "model_id": display_id,
            "input_price": round(pricing["input_price"], 6),
            "output_price": round(pricing["output_price"], 6),
            "max_tokens": entry.get("max_tokens"),
            "max_input_tokens": entry.get("max_input_tokens"),
            "litellm_provider": entry.get("litellm_provider"),
        })

        if len(results) >= limit:
            break

    # Sort: exact matches first, then by key length (shorter = more canonical)
    results.sort(key=lambda x: (
        0 if x["model_id"].lower() == search_lower else 1,
        len(x["model_id"]),
    ))

    return results
