import argparse
import sys
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from tabulate import tabulate
import pytz  
from tzlocal import get_localzone 
sys.path.append('.')

from app.db.database import SessionLocal
from app.models.provider import ApiKeyUsage, Model, ModelProvider, ModelImplementation, ApiKey

def parse_args():
    parser = argparse.ArgumentParser(description='Token usage statistics')
    parser.add_argument('--by', choices=['day', 'hour'], default='day',
                       help='Group statistics by day or hour')
    parser.add_argument('--group', choices=['model', 'provider', 'key'],
                       default='model', help='Group results by model, provider, or API key')
    parser.add_argument('--from', dest='from_date', type=str,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--to', dest='to_date', type=str,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--today', action='store_true',
                       help='Show only today\'s statistics')
    return parser.parse_args()

def get_date_filter(args):
    if args.today:
        today = datetime.now().date()
        return (func.date(ApiKeyUsage.timestamp) == today)
    elif args.from_date or args.to_date:
        filters = []
        if args.from_date:
            from_date = datetime.strptime(args.from_date, '%Y-%m-%d').date()
            filters.append(func.date(ApiKeyUsage.timestamp) >= from_date)
        if args.to_date:
            to_date = datetime.strptime(args.to_date, '%Y-%m-%d').date()
            filters.append(func.date(ApiKeyUsage.timestamp) <= to_date)
        return tuple(filters)
    else:
        # Default to last 7 days including today
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=6)  # 6 days ago + today = 7 days
        return (
            func.date(ApiKeyUsage.timestamp) >= seven_days_ago,
            func.date(ApiKeyUsage.timestamp) <= today
        )

def get_usage_stats(db: Session, args):
    # 1. 确定基础查询列
    base_columns = [ModelProvider.name.label('provider_name')]
    if args.group == 'key':
        base_columns.append(ApiKey.alias.label('key_name'))
    else:  # model
        base_columns.extend([
            Model.name.label('model_name')
        ])
    
    # 添加时间和总token数
    if args.by == 'hour':
        base_columns.append(func.timezone('UTC', func.date_trunc('hour', ApiKeyUsage.timestamp)).label('timestamp'))
    else:
        base_columns.append(func.timezone('UTC', func.date(ApiKeyUsage.timestamp)).label('timestamp'))
    
    base_columns.append(func.sum(ApiKeyUsage.total_tokens).label('total_tokens'))
    
    # 2. 构建查询
    query = db.query(*base_columns)
    
    # 3. 添加必要的表连接
    query = query.join(
        ModelImplementation, ApiKeyUsage.model_implementation_id == ModelImplementation.id
    )
    
    if args.group != 'key':
        # 如果不按key分组，需要连接Model和Provider表
        query = query.join(
            Model, ModelImplementation.model_id == Model.id
        ).join(
            ModelProvider, ModelImplementation.provider_id == ModelProvider.id
        )
    else:
        # 如果按key分组，需要连接ApiKey表
        query = query.join(
            ApiKey, ApiKeyUsage.api_key_id == ApiKey.id
        ).join(
            ModelProvider, ApiKey.provider_id == ModelProvider.id
        )
    
    # 4. 添加日期过滤条件
    date_filter = get_date_filter(args)
    if date_filter is not None:
        if isinstance(date_filter, tuple):
            for f in date_filter:
                query = query.filter(f)
        else:
            query = query.filter(date_filter)
    
    # 5. 添加分组和排序
    group_by_columns = []
    
    # 按时间分组
    if args.by == 'hour':
        group_by_columns.append(func.date_trunc('hour', ApiKeyUsage.timestamp))
    else:
        group_by_columns.append(func.date(ApiKeyUsage.timestamp))
    
    # 按指定字段分组
    group_by_columns.append(ModelProvider.name)
    if args.group == 'key':
        group_by_columns.append(ApiKey.alias)
    else:  # model
        group_by_columns.append(Model.name)
    
    query = query.group_by(*group_by_columns)
    
    # 添加排序
    if args.by == 'hour':
        query = query.order_by(func.date_trunc('hour', ApiKeyUsage.timestamp))
    else:
        query = query.order_by(func.date(ApiKeyUsage.timestamp))

    from sqlalchemy.dialects import postgresql
    sql_query = query.statement.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={"literal_binds": True}
    )
    print(f"\nGenerated SQL query:\n{sql_query}")
    return query.all()

def display_stats(stats, args):
    # Group stats by timestamp
    grouped_stats = {}
    total_tokens = 0
    local_tz = get_localzone()
    
    for row in stats:
        timestamp = row.timestamp
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is None:
            # 先将naive datetime解释为UTC
            aware_timestamp = pytz.utc.localize(timestamp)
            # 然后转换为本地时区
            timestamp = aware_timestamp.astimezone(local_tz)
        
        if timestamp not in grouped_stats:
            grouped_stats[timestamp] = []
        grouped_stats[timestamp].append(row)
        total_tokens += row.total_tokens

    # Display header with date range
    if args.from_date and args.to_date:
        date_range = f"日期范围: {args.from_date} 至 {args.to_date}"
    elif args.today:
        date_range = f"日期: {datetime.now().strftime('%Y-%m-%d')}"
    else:
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=6)
        date_range = f"日期范围: {seven_days_ago.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}"
    
    print(date_range)
    print()

    # Display a separate table for each timestamp
    for timestamp, rows in sorted(grouped_stats.items()):
        if args.by == 'hour':
            date_str = timestamp.strftime('%Y-%m-%d %H:00')
        else:
            date_str = timestamp.strftime('%Y-%m-%d')
        
        print(f"===== {date_str} =====")
        
        if args.group == 'provider':
            table_data = [
                [row.provider_name, row.total_tokens]
                for row in rows
            ]
            headers = ["提供商", "Token 数"]
        elif args.group == 'key':
            table_data = [
                [row.provider_name, row.key_name, row.total_tokens]
                for row in rows
            ]
            headers = ["提供商","API Key", "Token 数"]
        else:
            table_data = [
                [row.model_name, row.provider_name, row.total_tokens]
                for row in rows
            ]
            headers = ["模型", "提供商", "Token 数"]
        
        # Calculate subtotal for this timestamp
        subtotal = sum(row.total_tokens for row in rows)
        
        print(tabulate(table_data, headers=headers,
                      tablefmt="grid", stralign="left"))
        print(f"小计: {subtotal} tokens")
        print()  # Add empty line between tables
    
    print(f"总计: {total_tokens} tokens")

def main():
    args = parse_args()
    db = SessionLocal()
    try:
        stats = get_usage_stats(db, args)
        display_stats(stats, args)
    finally:
        db.close()

if __name__ == "__main__":
    main()
