import streamlit as st
import pandas as pd
import altair as alt

# إعداد الصفحة
st.set_page_config(page_title="تقرير المبيعات", layout="wide")
st.title("📊 تقرير المبيعات اليومية")

# تحميل البيانات
try:
    df = pd.read_csv("sales.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # حذف الأعمدة الزائدة
    df = df[df["Name"].notna()]  # حذف الصفوف الفارغة
    df = df[df["Name"] != "Total"]  # حذف صف الإجمالي
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")  # تنظيف القيم
    df["Sales%"] = df["Sales%"].astype(str).str.replace('%', '').str.replace(',', '').astype(float)
    df["Customer%"] = df["Customer%"].astype(str).str.replace('%', '').str.replace(',', '').astype(float)
except Exception as e:
    st.error(f"❌ خطأ في تحميل الملف: {e}")
    st.stop()

# زر تحميل التقرير
st.download_button(
    label="📥 تحميل التقرير كـ CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="تقرير_المبيعات.csv",
    mime="text/csv"
)

# مؤشرات عامة
col1, col2, col3 = st.columns(3)
col1.metric("📈 إجمالي المبيعات", f"{df['Sales'].sum():,.0f}")
col2.metric("📉 متوسط المبيعات", f"{df['Sales'].mean():,.0f}")
col3.metric("🔥 أعلى مبيعات", f"{df['Sales'].max():,.0f}")

# فلترة حسب المندوب أو المدينة
salesmen = df["Name"].dropna().unique()
cities = df["City"].dropna().unique()

with st.sidebar:
    st.header("🎯 فلترة البيانات")
    selected_salesman = st.selectbox("👤 اختر مندوب المبيعات", options=["الكل"] + sorted(salesmen))
    selected_city = st.selectbox("🏙️ اختر المدينة", options=["الكل"] + sorted(cities))

filtered_df = df.copy()
if selected_salesman != "الكل":
    filtered_df = filtered_df[filtered_df["Name"] == selected_salesman]
if selected_city != "الكل":
    filtered_df = filtered_df[filtered_df["City"] == selected_city]

# تلوين حسب نسبة المبيعات
def highlight_sales(val):
    try:
        val = float(val)
        if val >= 40:
            return 'background-color: #d4f4dd'
        elif val >= 30:
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #f8d7da'
    except:
        return ''

styled_df = filtered_df.style.applymap(highlight_sales, subset=["Sales%"])
st.subheader("📋 جدول المبيعات")
st.dataframe(styled_df, use_container_width=True)

# رسم بياني حسب المندوب
st.subheader("📊 نسبة الإنجاز حسب المندوب")
sales_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X("Name", sort="-y", title="مندوب المبيعات"),
    y=alt.Y("Sales%", title="نسبة المبيعات"),
    color=alt.Color("Sales%", scale=alt.Scale(scheme="greens")),
    tooltip=["Name", "City", "Sales%", "Sales"]
).properties(width=700, height=400)

st.altair_chart(sales_chart, use_container_width=True)

# رسم بياني حسب المدينة
st.subheader("🏙️ نسبة الإنجاز حسب المدينة")
city_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X("City", sort="-y", title="المدينة"),
    y=alt.Y("Sales%", title="نسبة المبيعات"),
    color=alt.Color("Sales%", scale=alt.Scale(scheme="blues")),
    tooltip=["City", "Sales%", "Sales"]
).properties(width=700, height=400)

st.altair_chart(city_chart, use_container_width=True)