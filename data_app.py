import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import plotly.express as px

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    categories = Column(String, index=True)
    sentiment = Column(String, index=True)


def get_top_categories(db: Session):
    return (
        db.query(Item.categories, func.count(Item.categories).label("count"))
        .group_by(Item.categories)
        .order_by(func.count(Item.categories).desc())
        .limit(10)
        .all()
    )


def main():
    st.title("Sentiment and Topic Classification from datasources")

    # Create a database session
    db = SessionLocal()
    top_categories = get_top_categories(db)

    # Close the database session
    db.close()

    # Display the results in Streamlit
    if top_categories:
        st.subheader("Topic Classification")
        categories = [category for category, count in top_categories]
        counts = [count for category, count in top_categories]

        # Create a bar chart
        data = {"Topic": categories, "Count": counts}
        df = pd.DataFrame(data)
        df.index = df.index + 1  # Start counting from 1
        df = df.sort_values(by="Count", ascending=False)
        st.table(df)

        st.subheader("Sentiment Distribution")

        # Query the sentiment distribution from the database
        sentiment_distribution = (
            db.query(Item.sentiment, func.count(Item.sentiment).label("count"))
            .group_by(Item.sentiment)
            .all()
        )

        if sentiment_distribution:
            sentiments = [sentiment for sentiment, count in sentiment_distribution]
            sentiment_counts = [count for sentiment, count in sentiment_distribution]

            # Create a pie chart
            sentiment_data = {"Sentiment": sentiments, "Count": sentiment_counts}
            sentiment_df = pd.DataFrame(sentiment_data)
            colors = {'positive': 'lightgreen', 'negative': 'lightcoral'}
            fig = px.pie(sentiment_df, names='Sentiment', values='Count', title='Sentiment Distribution', color='Sentiment', color_discrete_map=colors)
            st.plotly_chart(fig)

        st.subheader("User Happiness")

        # Query the user happiness distribution from the database
        happiness_distribution = (
            db.query(Item.user, Item.sentiment, func.count(Item.sentiment).label("count"))
            .group_by(Item.user, Item.sentiment)
            .all()
        )

        if happiness_distribution:
            happiness = ["Happy" if sentiment.lower() == "positive" else "Unhappy" for user, sentiment, count in happiness_distribution]
            users = [user for user, sentiment, count in happiness_distribution]
            happiness_counts = [count for user, sentiment, count in happiness_distribution]

            # Create a table
            happiness_data = {"User": users, "Happiness": happiness, "Incidents": happiness_counts}
            happiness_df = pd.DataFrame(happiness_data)
            happiness_df.index = happiness_df.index + 1  # Start counting from 1
            st.table(happiness_df)

        # Calculate the overall product love percentage
        total_responses = sum(happiness_counts)
        happy_responses = sum(count for user, sentiment, count in happiness_distribution if sentiment.lower() == "positive")
        love_percentage = (happy_responses / total_responses) * 100 if total_responses > 0 else 0

        if love_percentage < 50:
            st.markdown(f"<h3 style='color: red;'>Overall Product Love Percentage: {love_percentage:.2f}%</h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: green;'>Overall Product Love Percentage: {love_percentage:.2f}%</h3>", unsafe_allow_html=True)
    else:
        st.write("No data available.")


if __name__ == "__main__":
    main()
