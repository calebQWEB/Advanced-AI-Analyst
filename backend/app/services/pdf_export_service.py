import os
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from io import BytesIO
import tempfile
from app.utils.logger import logger

class PDFExportService:
    def __init__(self):
        # Define color scheme
        self.colors = {
            'primary': HexColor('#2563EB'),      # Blue
            'secondary': HexColor('#10B981'),    # Green
            'accent': HexColor('#F59E0B'),       # Orange
            'danger': HexColor('#EF4444'),       # Red
            'dark': HexColor('#1F2937'),         # Dark Gray
            'light': HexColor('#F3F4F6'),        # Light Gray
            'white': HexColor('#FFFFFF')
        }
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.colors['dark'],
            spaceAfter=15,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=self.colors['primary'],
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=self.colors['primary'],
            borderPadding=5,
            backColor=self.colors['light']
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=self.colors['secondary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Small text style
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.colors['dark'],
            spaceAfter=5
        ))

    async def generate_insights_pdf(
        self, 
        insights: Dict[str, Any], 
        file_name: str,
        user_id: str
    ) -> bytes:
        """Generate a comprehensive PDF report from insights data"""
        try:
            # Create a temporary file for the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the story (content)
            story = []
            
            # Add header
            story.extend(self._create_header(file_name))
            
            # Add executive summary
            story.extend(self._create_executive_summary(insights))
            
            # Add dataset overview
            if 'dataset_info' in insights:
                story.extend(self._create_dataset_overview(insights['dataset_info']))
            
            # Add sales analysis
            if 'top_sales_reps' in insights or 'sales_metrics' in insights:
                story.extend(self._create_sales_section(insights))
            
            # Add product analysis
            if 'top_products' in insights or 'revenue_by_category' in insights:
                story.extend(self._create_product_section(insights))
            
            # Add customer analysis
            if 'top_customers' in insights or 'customer_metrics' in insights:
                story.extend(self._create_customer_section(insights))
            
            # Add time analysis
            if 'monthly_trends' in insights or 'daily_patterns' in insights:
                story.extend(self._create_time_analysis_section(insights))
            
            # Add regional analysis
            if 'regional_performance' in insights:
                story.extend(self._create_regional_section(insights))
            
            # Add revenue distribution
            if 'revenue_distribution' in insights:
                story.extend(self._create_revenue_distribution_section(insights))
            
            # Add footer
            story.extend(self._create_footer())
            
            # Build PDF
            doc.build(story)
            
            # Read the PDF content
            with open(pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            # Clean up temporary file
            os.unlink(pdf_path)
            
            logger.info("PDF report generated successfully", user_id=user_id, file_name=file_name)
            return pdf_content
            
        except Exception as e:
            logger.error("Failed to generate PDF report", error=str(e), user_id=user_id)
            raise

    def _create_header(self, file_name: str) -> list:
        """Create PDF header section"""
        content = []
        
        # Title
        content.append(Paragraph(
            "📊 Data Analysis Report",
            self.styles['CustomTitle']
        ))
        
        # File name
        content.append(Paragraph(
            f"Analysis of: <b>{file_name}</b>",
            self.styles['CustomSubtitle']
        ))
        
        # Generation date
        content.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['SmallText']
        ))
        
        content.append(Spacer(1, 20))
        
        return content

    def _create_executive_summary(self, insights: Dict[str, Any]) -> list:
        """Create executive summary section"""
        content = []
        
        content.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Key metrics cards
        metrics = []
        
        if 'sales_metrics' in insights:
            sales_metrics = insights['sales_metrics']
            metrics.extend([
                [
                    "Total Revenue",
                    f"${sales_metrics.get('total_revenue', 0):,.2f}",
                    "📈"
                ],
                [
                    "Total Transactions", 
                    f"{sales_metrics.get('total_transactions', 0):,}",
                    "🛍️"
                ],
                [
                    "Average Transaction",
                    f"${sales_metrics.get('average_transaction', 0):,.2f}",
                    "💰"
                ]
            ])
        
        if 'customer_metrics' in insights:
            customer_metrics = insights['customer_metrics']
            metrics.append([
                "Total Customers",
                f"{customer_metrics.get('total_customers', 0):,}",
                "👥"
            ])
        
        if metrics:
            # Create metrics table
            table_data = []
            for i in range(0, len(metrics), 3):
                row = []
                for j in range(3):
                    if i + j < len(metrics):
                        metric = metrics[i + j]
                        cell_content = f"{metric[2]}<br/><b>{metric[1]}</b><br/>{metric[0]}"
                        row.append(Paragraph(cell_content, self.styles['Normal']))
                    else:
                        row.append("")
                table_data.append(row)
            
            if table_data:
                metrics_table = Table(table_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, -1), self.colors['light']),
                    ('BOX', (0, 0), (-1, -1), 1, self.colors['primary']),
                    ('INNERGRID', (0, 0), (-1, -1), 1, self.colors['primary']),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 15),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ]))
                content.append(metrics_table)
        
        content.append(Spacer(1, 20))
        return content

    def _create_dataset_overview(self, dataset_info: Dict[str, Any]) -> list:
        """Create dataset overview section"""
        content = []
        
        content.append(Paragraph("Dataset Overview", self.styles['SectionHeader']))
        
        # Dataset stats table
        data = [
            ['Metric', 'Value'],
            ['Total Rows', f"{dataset_info['total_rows']:,}"],
            ['Total Columns', f"{dataset_info['total_columns']:,}"],
            ['Columns Mapped', f"{dataset_info['columns_mapped']:,}"],
            ['Data Completeness', f"{dataset_info['data_completeness']}%"]
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary'])
        ]))
        
        content.append(table)
        content.append(Spacer(1, 15))
        
        return content

    def _create_sales_section(self, insights: Dict[str, Any]) -> list:
        """Create sales analysis section"""
        content = []
        
        content.append(Paragraph("Sales Performance Analysis", self.styles['SectionHeader']))
        
        # Top performers
        if 'top_sales_reps' in insights and insights['top_sales_reps'].get('all_reps'):
            content.append(Paragraph("🏆 Top Sales Representatives", self.styles['Normal']))
            
            # Create table for top sales reps
            headers = ['Rank', 'Sales Rep', 'Total Sales', 'Transactions', 'Avg Transaction']
            table_data = [headers]
            
            for idx, rep in enumerate(insights['top_sales_reps']['all_reps'][:10], 1):
                # Safely get values with defaults
                rep_name = str(rep.get('name', 'Unknown Rep'))
                total_sales = rep.get('total_sales', 0)
                transactions = rep.get('transactions', 0)
                avg_transaction = rep.get('avg_transaction', 0)
                
                table_data.append([
                    str(idx),
                    rep_name,
                    f"${total_sales:,.2f}",
                    str(transactions),
                    f"${avg_transaction:,.2f}"
                ])
            
            sales_table = Table(table_data, colWidths=[0.6*inch, 2*inch, 1.5*inch, 1*inch, 1.4*inch])
            sales_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
                ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['primary']),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            content.append(sales_table)
        
        # Only add spacer if we actually added content
        if len(content) > 1:  # More than just the header
            content.append(Spacer(1, 15))
        
        return content

    def _create_product_section(self, insights: Dict[str, Any]) -> list:
        """Create product analysis section"""
        content = []
        
        content.append(Paragraph("Product Performance Analysis", self.styles['SectionHeader']))
        
        # Top products
        if 'top_products' in insights and insights['top_products']:
            content.append(Paragraph("🎯 Best Selling Products", self.styles['Normal']))
            
            headers = ['Rank', 'Product', 'Revenue', 'Units Sold', 'Avg Revenue/Sale']
            table_data = [headers]
            
            for idx, product in enumerate(insights['top_products'][:10], 1):
                # Safely get values with defaults
                product_name = str(product.get('name', 'Unknown Product'))
                total_revenue = product.get('total_revenue', 0)
                units_sold = product.get('units_sold', 0)
                avg_revenue_per_sale = product.get('avg_revenue_per_sale', 0)
                
                # Truncate long product names
                display_name = product_name[:30] + "..." if len(product_name) > 30 else product_name
                
                table_data.append([
                    str(idx),
                    display_name,
                    f"${total_revenue:,.2f}",
                    str(units_sold),
                    f"${avg_revenue_per_sale:,.2f}"
                ])
            
            products_table = Table(table_data, colWidths=[0.6*inch, 2.5*inch, 1.3*inch, 1*inch, 1.1*inch])
            products_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
                ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary']),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            content.append(products_table)
        
        # Category performance
        if 'revenue_by_category' in insights and insights['revenue_by_category']:
            content.append(Spacer(1, 10))
            content.append(Paragraph("📊 Revenue by Category", self.styles['Normal']))
            
            headers = ['Category', 'Revenue', 'Transactions', 'Revenue %']
            table_data = [headers]
            
            total_revenue = sum(cat.get('revenue', 0) for cat in insights['revenue_by_category'])
            
            for category in insights['revenue_by_category'][:8]:
                cat_revenue = category.get('revenue', 0)
                cat_transactions = category.get('transactions', 0)
                revenue_percent = (cat_revenue / total_revenue * 100) if total_revenue > 0 else 0
                
                table_data.append([
                    str(category.get('category', 'Unknown')),
                    f"${cat_revenue:,.2f}",
                    str(cat_transactions),
                    f"{revenue_percent:.1f}%"
                ])
            
            category_table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
                ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['accent']),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            content.append(category_table)
        
        # Only add spacer if we actually added content
        if len(content) > 1:  # More than just the header
            content.append(Spacer(1, 15))
        
        return content

    def _create_customer_section(self, insights: Dict[str, Any]) -> list:
        """Create customer analysis section"""
        content = []
        
        content.append(Paragraph("Customer Analysis", self.styles['SectionHeader']))
        
        # Top customers
        if 'top_customers' in insights and insights['top_customers']:
            content.append(Paragraph("💎 Top Valued Customers", self.styles['Normal']))
            
            headers = ['Rank', 'Customer', 'Total Spent', 'Transactions', 'Avg Transaction']
            table_data = [headers]
            
            for idx, customer in enumerate(insights['top_customers'][:10], 1):
                # Safely get values with defaults
                customer_name = str(customer.get('name', 'Unknown Customer'))
                total_spent = customer.get('total_spent', 0)
                transactions = customer.get('transactions', 0)
                avg_transaction = customer.get('avg_transaction', 0)
                
                # Truncate long customer names
                display_name = customer_name[:25] + "..." if len(customer_name) > 25 else customer_name
                
                table_data.append([
                    str(idx),
                    display_name,
                    f"${total_spent:,.2f}",
                    str(transactions),
                    f"${avg_transaction:,.2f}"
                ])
            
            customer_table = Table(table_data, colWidths=[0.6*inch, 2.2*inch, 1.4*inch, 1*inch, 1.3*inch])
            customer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
                ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['primary']),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            content.append(customer_table)
        
        # Customer insights
        if 'customer_metrics' in insights:
            content.append(Spacer(1, 10))
            content.append(Paragraph("📈 Customer Insights", self.styles['Normal']))
            
            metrics = insights['customer_metrics']
            concentration = metrics.get('customer_concentration', {})
            
            insights_text = f"""
            <b>Key Customer Metrics:</b><br/>
            • Average Customer Value: ${metrics.get('avg_customer_value', 0):,.2f}<br/>
            • Median Customer Value: ${metrics.get('median_customer_value', 0):,.2f}<br/>
            • Top Customer Value: ${metrics.get('top_customer_value', 0):,.2f}<br/>
            • Top 10% Revenue Share: {concentration.get('top_10_percent_revenue_share', 0):.1f}%<br/>
            • Top Customer Revenue Share: {concentration.get('top_customer_revenue_share', 0):.1f}%
            """
            
            content.append(Paragraph(insights_text, self.styles['Normal']))
        
        # Only add spacer if we actually added content
        if len(content) > 1:  # More than just the header
            content.append(Spacer(1, 15))
        
        return content

    def _create_time_analysis_section(self, insights: Dict[str, Any]) -> list:
        """Create time-based analysis section"""
        content = []
        
        content.append(Paragraph("Time-Based Analysis", self.styles['SectionHeader']))
        
        # Monthly trends
        if 'monthly_trends' in insights:
            content.append(Paragraph("📅 Monthly Performance Trends", self.styles['Normal']))
            
            headers = ['Month', 'Revenue', 'Transactions', 'Avg per Transaction']
            table_data = [headers]
            
            for trend in insights['monthly_trends'][-12:]:  # Last 12 months
                avg_per_transaction = trend['revenue'] / max(trend['transactions'], 1)
                table_data.append([
                    trend['month'],
                    f"${trend['revenue']:,.2f}",
                    str(trend['transactions']),
                    f"${avg_per_transaction:,.2f}"
                ])
            
            trends_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.3*inch])
            trends_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
                ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary']),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            content.append(trends_table)
        
        # Growth metrics
        if 'growth_metrics' in insights:
            content.append(Spacer(1, 10))
            growth = insights['growth_metrics']
            growth_text = f"""
            <b>Growth Analysis:</b><br/>
            • Monthly Growth Rate: {growth['monthly_growth_rate']}%<br/>
            • Trend Direction: {growth['trend_direction'].title()}<br/>
            """
            content.append(Paragraph(growth_text, self.styles['Normal']))
        
        content.append(Spacer(1, 15))
        return content

    def _create_regional_section(self, insights: Dict[str, Any]) -> list:
        """Create regional analysis section"""
        content = []
        
        content.append(Paragraph("Regional Performance", self.styles['SectionHeader']))
        
        if 'regional_performance' in insights:
            content.append(Paragraph("🌍 Performance by Region", self.styles['Normal']))
            
            headers = ['Region', 'Revenue', 'Market Share %', 'Transactions', 'Avg Transaction']
            table_data = [headers]
            
            for region in insights['regional_performance']:
                table_data.append([
                    region['region'],
                    f"${region['total_revenue']:,.2f}",
                    f"{region['revenue_share_percent']}%",
                    str(region['transactions']),
                    f"${region['avg_transaction']:,.2f}"
                ])
            
            regional_table = Table(table_data, colWidths=[1.5*inch, 1.3*inch, 1*inch, 1*inch, 1.2*inch])
            regional_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
                ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['accent']),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            content.append(regional_table)
        
        content.append(Spacer(1, 15))
        return content

    def _create_revenue_distribution_section(self, insights: Dict[str, Any]) -> list:
        """Create revenue distribution section"""
        content = []
        
        content.append(Paragraph("Revenue Distribution Analysis", self.styles['SectionHeader']))
        
        rev_dist = insights['revenue_distribution']
        
        # Statistical summary table
        headers = ['Statistic', 'Value']
        table_data = [
            headers,
            ['Minimum', f"${rev_dist['min']:,.2f}"],
            ['First Quartile (Q1)', f"${rev_dist['q1']:,.2f}"],
            ['Median', f"${rev_dist['median']:,.2f}"],
            ['Mean (Average)', f"${rev_dist['mean']:,.2f}"],
            ['Third Quartile (Q3)', f"${rev_dist['q3']:,.2f}"],
            ['Maximum', f"${rev_dist['max']:,.2f}"],
            ['Standard Deviation', f"${rev_dist['std_dev']:,.2f}"]
        ]
        
        stats_table = Table(table_data, colWidths=[2.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['light']),
            ('ALTERNATE', (0, 1), (-1, -1), self.colors['white']),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary']),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        content.append(stats_table)
        content.append(Spacer(1, 15))
        
        return content

    def _create_footer(self) -> list:
        """Create PDF footer"""
        content = []
        
        content.append(Spacer(1, 30))
        
        # Footer text
        footer_text = f"""
        <b>Report generated by AI Data Analyst</b><br/>
        This automated analysis provides insights based on your data patterns and trends.<br/>
        For questions or additional analysis, please contact support.
        """
        
        content.append(Paragraph(footer_text, self.styles['SmallText']))
        
        return content