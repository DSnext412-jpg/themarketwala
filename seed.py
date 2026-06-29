import datetime
from app import create_app
from extensions import db
from models.user import User
from models.course import Course
from models.blog import Blog
from models.notification import Notification


def seed_data():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.filter_by(email='dipaksonwane412@gmail.com').first():
            print('Admin user already exists. Skipping seed.')
            return

        admin = User(
            name='Dipak Sonwane',
            email='dipaksonwane412@gmail.com',
            role='admin',
            experience_level='advanced',
            interests='Trading, Investing, Technical Analysis, Financial Markets'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

        demo_student = User(
            name='Demo Student',
            email='student@demo.com',
            role='student',
            experience_level='beginner',
            interests='Stock Market, Trading'
        )
        demo_student.set_password('Student@123')
        db.session.add(demo_student)

        courses_data = [
            {
                'title': 'Stock Market Masterclass',
                'slug': 'stock-market-masterclass',
                'description': 'A complete A-Z course on stock market trading and investing. Learn technical analysis, fundamental analysis, risk management, and trading psychology.',
                'content': """# Stock Market Masterclass

## Module 1: Introduction to Stock Markets

Welcome to the Stock Market Masterclass! This comprehensive course will take you from a complete beginner to a confident trader.

### What You'll Learn

- How the stock market works
- Types of trading (Intraday, Swing, Positional)
- Technical Analysis basics
- Fundamental Analysis
- Risk Management

### Key Concepts

> "The stock market is a device for transferring money from the impatient to the patient." - Warren Buffett

1. **Market Structure** - Understanding how exchanges work
2. **Trading vs Investing** - The key differences
3. **Risk Management** - The most important skill

| Concept | Time to Master | Difficulty |
|---------|---------------|------------|
| Market Basics | 1 Week | Beginner |
| Technical Analysis | 3 Weeks | Intermediate |
| Advanced Strategies | 4 Weeks | Advanced |

## Module 2: Technical Analysis

```python
# Simple Moving Average Crossover Strategy
def sma_crossover(prices, short_window=20, long_window=50):
    short_sma = prices.rolling(window=short_window).mean()
    long_sma = prices.rolling(window=long_window).mean()
    return short_sma > long_sma
```

## Module 3: Risk Management

- Never risk more than 2% per trade
- Always use stop-loss
- Maintain a trading journal
""",
                'category': 'masterclass',
                'difficulty': 'beginner',
                'price': 4999,
                'reading_time': '12 hours',
                'lecture_times': 'Session 1: Market Basics\nSession 2: Technical Analysis\nSession 3: Chart Patterns\nSession 4: Risk Management\nSession 5: Live Trading\nSession 6: Psychology & Review',
                'drive_link': 'https://drive.google.com/',
                'live_meeting_link': 'https://meet.google.com/',
                'tags': 'stock market, trading, investing, technical analysis, beginner',
                'is_published': True,
            },
            {
                'title': 'Advanced Technical Analysis',
                'slug': 'advanced-technical-analysis',
                'description': 'Master advanced chart patterns, indicators, and price action strategies used by professional traders.',
                'content': '# Advanced Technical Analysis\n\n## Advanced Chart Patterns\n\nLearn complex patterns like harmonic patterns, elliott wave, and advanced candlestick formations.',
                'category': 'technical',
                'difficulty': 'advanced',
                'price': 7999,
                'reading_time': '16 hours',
                'tags': 'technical analysis, advanced, chart patterns, indicators',
                'is_published': True,
            },
            {
                'title': 'Fundamental Analysis Pro',
                'slug': 'fundamental-analysis-pro',
                'description': 'Learn how to analyze company financials, read balance sheets, and identify undervalued stocks.',
                'content': '# Fundamental Analysis Pro\n\n## Reading Financial Statements\n\nUnderstanding balance sheets, income statements, and cash flow statements.',
                'category': 'fundamental',
                'difficulty': 'intermediate',
                'price': 3999,
                'reading_time': '8 hours',
                'tags': 'fundamental, analysis, financials, value investing',
                'is_published': True,
            },
        ]

        for c_data in courses_data:
            course = Course(**c_data)
            db.session.add(course)

        blogs_data = [
            {
                'title': '5 Essential Risk Management Rules for Beginners',
                'slug': 'risk-management-rules-beginners',
                'content': """# 5 Essential Risk Management Rules for Beginners

Risk management is the single most important skill in trading. Without it, even the best strategy will fail.

## Rule 1: The 2% Rule
Never risk more than 2% of your capital on a single trade.

## Rule 2: Always Use Stop Loss
A stop loss is your safety net. Never enter a trade without one.

## Rule 3: Maintain a Trading Journal
Write down every trade, including your reasoning and emotions.

> "The goal of a successful trader is to make the best trades. Money is secondary." - Alexander Elder

## Rule 4: Diversify Your Portfolio
Don't put all your eggs in one basket.

## Rule 5: Keep Learning
The market evolves. So should you.
""",
                'excerpt': 'Risk management is the single most important skill in trading. Here are 5 rules every beginner must follow to protect their capital and trade successfully.',
                'seo_title': 'Risk Management Rules for Beginner Traders',
                'seo_description': 'Learn the 5 essential risk management rules every beginner trader must follow to protect capital and trade successfully.',
                'is_published': True,
            },
            {
                'title': 'Understanding Market Cycles',
                'slug': 'understanding-market-cycles',
                'content': '# Understanding Market Cycles\n\nMarkets move in cycles. Understanding where we are in the cycle can help you make better trading decisions.',
                'excerpt': 'Markets move in predictable cycles. Learn to identify accumulation, markup, distribution, and markdown phases.',
                'seo_title': 'Understanding Stock Market Cycles',
                'seo_description': 'Learn to identify the four phases of market cycles and make better trading decisions.',
                'is_published': True,
            },
        ]

        for b_data in blogs_data:
            blog = Blog(**b_data)
            db.session.add(blog)

        db.session.commit()
        print('Seed data created successfully!')
        print(f'Admin: dipaksonwane412@gmail.com / Admin@123')
        print(f'Demo: student@demo.com / Student@123')


if __name__ == '__main__':
    seed_data()
