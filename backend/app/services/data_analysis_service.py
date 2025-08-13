import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from app.utils.logger import logger
import re

class DataAnalysisService:
    def __init__(self):
        # Define comprehensive column patterns for better matching
        self.column_patterns = {
            'sales_rep': [
                ['sales', 'rep'], ['sales', 'person'], ['salesperson'], 
                ['rep'], ['agent'], ['sales', 'agent'], ['account', 'manager']
            ],
            'revenue': [
                ['total', 'price'], ['total', 'sale'], ['total', 'sales'], 
                ['total', 'amount'], ['total', 'cost'], ['total', 'value'],
                ['revenue'], ['sales', 'amount'], ['amount'], ['price', 'total'],
                ['sale', 'total'], ['gross', 'sales'], ['net', 'sales']
            ],
            'product': [
                ['product'], ['item'], ['merchandise'], ['sku'], 
                ['product', 'name'], ['item', 'name']
            ],
            'category': [
                ['category'], ['product', 'category'], ['item', 'category'],
                ['type'], ['product', 'type'], ['class'], ['group']
            ],
            'quantity': [
                ['quantity'], ['qty'], ['units'], ['amount', 'sold'], 
                ['units', 'sold'], ['count'], ['volume']
            ],
            'customer': [
                ['customer'], ['client'], ['buyer'], ['customer', 'name'],
                ['client', 'name'], ['account'], ['purchaser']
            ],
            'date': [
                ['date'], ['time'], ['timestamp'], ['order', 'date'],
                ['sale', 'date'], ['transaction', 'date'], ['created']
            ],
            'region': [
                ['region'], ['location'], ['state'], ['country'], 
                ['city'], ['territory'], ['area'], ['zone'], ['market']
            ]
        }

    def compute_business_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute actual business insights from the dataframe"""
        try:
            if df.empty:
                logger.warning("Empty dataframe provided")
                return {}
                
            insights = {}
            logger.info(f"Analyzing dataframe with columns: {list(df.columns)}")
            
            # Get column mappings
            column_mappings = self._map_columns(df)
            logger.info(f"Column mappings found: {column_mappings}")
            
            # Sales analysis
            if self._can_analyze_sales(column_mappings):
                insights.update(self._analyze_sales_data(df, column_mappings))
                logger.info("Sales analysis completed")
            
            # Product analysis
            if self._can_analyze_products(column_mappings):
                insights.update(self._analyze_product_data(df, column_mappings))
                logger.info("Product analysis completed")
            
            # Customer analysis
            if self._can_analyze_customers(column_mappings):
                insights.update(self._analyze_customer_data(df, column_mappings))
                logger.info("Customer analysis completed")
            
            # Time-based analysis
            if self._can_analyze_time(column_mappings):
                insights.update(self._analyze_time_data(df, column_mappings))
                logger.info("Time analysis completed")
            
            # Regional analysis
            if self._can_analyze_regions(column_mappings):
                insights.update(self._analyze_regional_data(df, column_mappings))
                logger.info("Regional analysis completed")
            
            # Add basic statistics
            insights.update(self._get_basic_stats(df, column_mappings))
            
            logger.info("Business insights computed successfully")
            return insights
            
        except Exception as e:
            logger.error("Failed to compute business insights", error=str(e))
            return {}

    def _map_columns(self, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """Map dataframe columns to business concepts using flexible pattern matching"""
        columns_lower = {col.lower(): col for col in df.columns}
        mappings = {}
        
        for concept, patterns in self.column_patterns.items():
            best_match = None
            best_score = 0
            
            for col_lower, col_original in columns_lower.items():
                for pattern in patterns:
                    score = self._calculate_match_score(col_lower, pattern)
                    if score > best_score and score > 0.6:  # Minimum threshold
                        # Additional validation for numeric columns where needed
                        if concept in ['revenue', 'quantity'] and not pd.api.types.is_numeric_dtype(df[col_original]):
                            continue
                        best_match = col_original
                        best_score = score
            
            mappings[concept] = best_match
        
        return mappings

    def _calculate_match_score(self, column_name: str, pattern: List[str]) -> float:
        """Calculate how well a column name matches a pattern"""
        # Remove common separators and normalize
        normalized_col = re.sub(r'[_\-\s]+', ' ', column_name.lower()).strip()
        
        # Check if all pattern words are present
        words_found = 0
        total_pattern_length = sum(len(word) for word in pattern)
        matched_length = 0
        
        for word in pattern:
            if word in normalized_col:
                words_found += 1
                matched_length += len(word)
            elif any(word in part for part in normalized_col.split()):
                words_found += 0.5  # Partial credit for partial word matches
                matched_length += len(word) * 0.5
        
        if words_found == 0:
            return 0.0
        
        # Calculate score based on word coverage and pattern completeness
        word_coverage = words_found / len(pattern)
        length_ratio = matched_length / max(len(normalized_col), total_pattern_length)
        
        # Bonus for exact matches
        exact_match_bonus = 1.0 if ' '.join(pattern) == normalized_col else 0.0
        
        return min(1.0, word_coverage * 0.7 + length_ratio * 0.2 + exact_match_bonus * 0.1)

    def _can_analyze_sales(self, mappings: Dict[str, Optional[str]]) -> bool:
        return mappings.get('sales_rep') is not None and mappings.get('revenue') is not None

    def _can_analyze_products(self, mappings: Dict[str, Optional[str]]) -> bool:
        return (mappings.get('product') is not None or mappings.get('category') is not None) and \
               mappings.get('revenue') is not None

    def _can_analyze_customers(self, mappings: Dict[str, Optional[str]]) -> bool:
        return mappings.get('customer') is not None and mappings.get('revenue') is not None

    def _can_analyze_time(self, mappings: Dict[str, Optional[str]]) -> bool:
        return mappings.get('date') is not None and mappings.get('revenue') is not None

    def _can_analyze_regions(self, mappings: Dict[str, Optional[str]]) -> bool:
        return mappings.get('region') is not None and mappings.get('revenue') is not None

    def _analyze_sales_data(self, df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Analyze sales representative performance"""
        insights = {}
        
        sales_rep_col = mappings['sales_rep']
        revenue_col = mappings['revenue']
        
        try:
            # Handle missing values
            df_clean = df.dropna(subset=[sales_rep_col, revenue_col])
            
            if df_clean.empty:
                logger.warning("No valid sales data after cleaning")
                return {}
            
            # Calculate sales by rep
            sales_by_rep = df_clean.groupby(sales_rep_col)[revenue_col].agg([
                'sum', 'count', 'mean', 'std'
            ]).round(2)
            
            # Handle NaN standard deviations
            sales_by_rep['std'] = sales_by_rep['std'].fillna(0)
            sales_by_rep = sales_by_rep.sort_values('sum', ascending=False)
            
            if not sales_by_rep.empty:
                insights['top_sales_reps'] = {
                    'best_performer': {
                        'name': str(sales_by_rep.index[0]),
                        'total_sales': float(sales_by_rep.iloc[0]['sum']),
                        'transactions': int(sales_by_rep.iloc[0]['count']),
                        'avg_transaction': float(sales_by_rep.iloc[0]['mean']),
                        'consistency': float(sales_by_rep.iloc[0]['std'])
                    },
                    'all_reps': [
                        {
                            'name': str(rep),
                            'total_sales': float(row['sum']),
                            'transactions': int(row['count']),
                            'avg_transaction': float(row['mean']),
                            'consistency': float(row['std'])
                        }
                        for rep, row in sales_by_rep.iterrows()
                    ]
                }
                
                # Calculate performance metrics
                total_revenue = float(df_clean[revenue_col].sum())
                insights['sales_metrics'] = {
                    'total_revenue': total_revenue,
                    'average_transaction': float(df_clean[revenue_col].mean()),
                    'median_transaction': float(df_clean[revenue_col].median()),
                    'total_transactions': len(df_clean),
                    'revenue_std_dev': float(df_clean[revenue_col].std())
                }
                
        except Exception as e:
            logger.error(f"Error in sales analysis: {str(e)}")
        
        return insights

    def _analyze_product_data(self, df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Analyze product performance"""
        insights = {}
        
        product_col = mappings.get('product')
        category_col = mappings.get('category')
        revenue_col = mappings['revenue']
        quantity_col = mappings.get('quantity')
        
        try:
            # Product analysis
            if product_col:
                df_clean = df.dropna(subset=[product_col, revenue_col])
                if not df_clean.empty:
                    product_metrics = df_clean.groupby(product_col).agg({
                        revenue_col: ['sum', 'count', 'mean'],
                        quantity_col: ['sum', 'mean'] if quantity_col else []
                    }).round(2)
                    
                    # Flatten column names
                    product_metrics.columns = ['_'.join(col).strip() for col in product_metrics.columns]
                    product_metrics = product_metrics.sort_values(f'{revenue_col}_sum', ascending=False)
                    
                    insights['top_products'] = []
                    for product, row in product_metrics.head(10).iterrows():
                        product_info = {
                            'name': str(product),
                            'total_revenue': float(row[f'{revenue_col}_sum']),
                            'units_sold': int(row[f'{revenue_col}_count']),
                            'avg_revenue_per_sale': float(row[f'{revenue_col}_mean'])
                        }
                        if quantity_col:
                            product_info['total_quantity'] = float(row[f'{quantity_col}_sum']) if f'{quantity_col}_sum' in row else 0
                        insights['top_products'].append(product_info)
            
            # Category analysis
            if category_col:
                df_clean = df.dropna(subset=[category_col, revenue_col])
                if not df_clean.empty:
                    category_revenue = df_clean.groupby(category_col)[revenue_col].agg(['sum', 'count']).round(2)
                    category_revenue = category_revenue.sort_values('sum', ascending=False)
                    
                    insights['revenue_by_category'] = [
                        {
                            'category': str(cat),
                            'revenue': float(row['sum']),
                            'transactions': int(row['count'])
                        }
                        for cat, row in category_revenue.iterrows()
                    ]
                    
        except Exception as e:
            logger.error(f"Error in product analysis: {str(e)}")
        
        return insights

    def _analyze_customer_data(self, df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Analyze customer behavior and value"""
        insights = {}
        
        customer_col = mappings['customer']
        revenue_col = mappings['revenue']
        
        try:
            df_clean = df.dropna(subset=[customer_col, revenue_col])
            if df_clean.empty:
                return {}
            
            customer_analysis = df_clean.groupby(customer_col)[revenue_col].agg([
                'sum', 'count', 'mean', 'std'
            ]).round(2)
            customer_analysis['std'] = customer_analysis['std'].fillna(0)
            customer_analysis = customer_analysis.sort_values('sum', ascending=False)
            
            insights['top_customers'] = [
                {
                    'name': str(customer),
                    'total_spent': float(row['sum']),
                    'transactions': int(row['count']),
                    'avg_transaction': float(row['mean']),
                    'spending_consistency': float(row['std'])
                }
                for customer, row in customer_analysis.head(10).iterrows()
            ]
            
            # Customer segmentation
            total_customers = len(customer_analysis)
            customer_values = customer_analysis['sum'].values
            
            insights['customer_metrics'] = {
                'total_customers': total_customers,
                'avg_customer_value': float(customer_analysis['sum'].mean()),
                'median_customer_value': float(customer_analysis['sum'].median()),
                'top_customer_value': float(customer_analysis.iloc[0]['sum']),
                'customer_concentration': {
                    'top_10_percent_revenue_share': float((customer_values[:max(1, total_customers//10)].sum() / customer_values.sum()) * 100) if total_customers > 0 else 0,
                    'top_customer_revenue_share': float((customer_values[0] / customer_values.sum()) * 100) if len(customer_values) > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in customer analysis: {str(e)}")
        
        return insights

    def _analyze_time_data(self, df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Analyze time-based trends"""
        insights = {}
        
        date_col = mappings['date']
        revenue_col = mappings['revenue']
        
        try:
            df_clean = df.dropna(subset=[date_col, revenue_col]).copy()
            if df_clean.empty:
                return {}
            
            # Convert to datetime with multiple format attempts
            date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
            
            for fmt in date_formats:
                try:
                    df_clean[date_col] = pd.to_datetime(df_clean[date_col], format=fmt)
                    break
                except:
                    continue
            else:
                # If no format works, try pandas' automatic parsing
                df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
            
            # Remove rows where date conversion failed
            df_clean = df_clean.dropna(subset=[date_col])
            
            if df_clean.empty:
                logger.warning("No valid dates found for time analysis")
                return {}
            
            # Monthly trends
            df_clean['month'] = df_clean[date_col].dt.to_period('M')
            monthly_revenue = df_clean.groupby('month')[revenue_col].agg(['sum', 'count']).round(2)
            
            insights['monthly_trends'] = [
                {
                    'month': str(month),
                    'revenue': float(row['sum']),
                    'transactions': int(row['count'])
                }
                for month, row in monthly_revenue.iterrows()
            ]
            
            # Growth calculations
            if len(monthly_revenue) > 1:
                revenue_values = monthly_revenue['sum'].values
                latest_month = revenue_values[-1]
                previous_month = revenue_values[-2]
                
                if previous_month != 0:
                    growth_rate = ((latest_month - previous_month) / previous_month) * 100
                    insights['growth_metrics'] = {
                        'monthly_growth_rate': round(float(growth_rate), 2),
                        'trend_direction': 'increasing' if growth_rate > 0 else 'decreasing'
                    }
            
            # Day of week analysis
            df_clean['day_of_week'] = df_clean[date_col].dt.day_name()
            daily_performance = df_clean.groupby('day_of_week')[revenue_col].agg(['sum', 'mean']).round(2)
            
            insights['daily_patterns'] = [
                {
                    'day': day,
                    'total_revenue': float(row['sum']),
                    'avg_revenue': float(row['mean'])
                }
                for day, row in daily_performance.iterrows()
            ]
            
        except Exception as e:
            logger.error(f"Error in time analysis: {str(e)}")
        
        return insights

    def _analyze_regional_data(self, df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Analyze regional performance"""
        insights = {}
        
        region_col = mappings['region']
        revenue_col = mappings['revenue']
        
        try:
            df_clean = df.dropna(subset=[region_col, revenue_col])
            if df_clean.empty:
                return {}
            
            regional_analysis = df_clean.groupby(region_col)[revenue_col].agg([
                'sum', 'count', 'mean', 'std'
            ]).round(2)
            regional_analysis['std'] = regional_analysis['std'].fillna(0)
            regional_analysis = regional_analysis.sort_values('sum', ascending=False)
            
            total_revenue = df_clean[revenue_col].sum()
            
            insights['regional_performance'] = [
                {
                    'region': str(region),
                    'total_revenue': float(row['sum']),
                    'transactions': int(row['count']),
                    'avg_transaction': float(row['mean']),
                    'revenue_share_percent': round(float((row['sum'] / total_revenue) * 100), 2),
                    'consistency': float(row['std'])
                }
                for region, row in regional_analysis.iterrows()
            ]
            
        except Exception as e:
            logger.error(f"Error in regional analysis: {str(e)}")
        
        return insights

    def _get_basic_stats(self, df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Get basic statistical information about the dataset"""
        stats = {
            'dataset_info': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns_mapped': len([v for v in mappings.values() if v is not None]),
                'data_completeness': round(float(df.count().sum() / (len(df) * len(df.columns))) * 100, 2)
            }
        }
        
        # Add revenue statistics if available
        if mappings.get('revenue'):
            revenue_col = mappings['revenue']
            revenue_data = df[revenue_col].dropna()
            if not revenue_data.empty:
                stats['revenue_distribution'] = {
                    'min': float(revenue_data.min()),
                    'max': float(revenue_data.max()),
                    'mean': round(float(revenue_data.mean()), 2),
                    'median': round(float(revenue_data.median()), 2),
                    'std_dev': round(float(revenue_data.std()), 2),
                    'q1': round(float(revenue_data.quantile(0.25)), 2),
                    'q3': round(float(revenue_data.quantile(0.75)), 2)
                }
        
        return stats