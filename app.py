import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบัญชีรายรับ-รายจ่าย", layout="wide")

# 2. ฟังก์ชันโหลดและบันทึกข้อมูล (ใช้ไฟล์ CSV แทน Database ง่ายๆ)
FILE_NAME = "data.csv"

def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        # ถ้ายังไม่มีไฟล์ ให้สร้างตารางว่างๆ รอไว้
        return pd.DataFrame(columns=["Date", "Item", "Category", "Type", "Amount"])

def save_data(date_in, item, category, type_in, amount):
    # โหลดข้อมูลเก่า
    df = load_data()
    # สร้างข้อมูลใหม่
    new_data = pd.DataFrame({
        "Date": [date_in],
        "Item": [item],
        "Category": [category],
        "Type": [type_in],
        "Amount": [amount]
    })
    # รวมร่างและบันทึกทับไฟล์เดิม
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    return df

# --- ส่วนของการแสดงผล (Frontend) ---

st.title("💰 My Income & Expense Tracker")

# 3. Sidebar: สำหรับกรอกข้อมูล
st.sidebar.header("📝 บันทึกรายการใหม่")
with st.sidebar.form("entry_form", clear_on_submit=True):
    date_input = st.date_input("วันที่", date.today())
    item_input = st.text_input("รายการ (เช่น ค่ากาแฟ)")
    type_input = st.selectbox("ประเภท", ["รายจ่าย", "รายรับ"])
    
    # เปลี่ยนตัวเลือกหมวดหมู่ตามประเภท (Logic ง่ายๆ)
    if type_input == "รายจ่าย":
        cat_options = ["อาหาร", "เดินทาง", "ช้อปปิ้ง", "บิล/สาธารณูปโภค", "อื่นๆ"]
    else:
        cat_options = ["เงินเดือน", "โบนัส", "ลงทุน", "อื่นๆ"]
        
    category_input = st.selectbox("หมวดหมู่", cat_options)
    amount_input = st.number_input("จำนวนเงิน", min_value=0.0, format="%.2f")
    
    submitted = st.form_submit_button("บันทึกข้อมูล")
    
    if submitted:
        save_data(date_input, item_input, category_input, type_input, amount_input)
        st.sidebar.success("บันทึกสำเร็จ!")

# 4. Main Dashboard: แสดงผลข้อมูล
df = load_data() # โหลดข้อมูลล่าสุดมาแสดง

if not df.empty:
    # --- ส่วนสรุปตัวเลข (Metrics) ---
    st.subheader("📊 ภาพรวมการเงิน")
    
    # คำนวณยอดรวม
    total_income = df[df["Type"] == "รายรับ"]["Amount"].sum()
    total_expense = df[df["Type"] == "รายจ่าย"]["Amount"].sum()
    balance = total_income - total_expense
    
    col1, col2, col3 = st.columns(3)
    col1.metric("รายรับรวม", f"฿{total_income:,.2f}", delta_color="normal")
    col2.metric("รายจ่ายรวม", f"฿{total_expense:,.2f}", delta="-inverse") # สีแดงถ้าเยอะ
    col3.metric("เงินคงเหลือ", f"฿{balance:,.2f}")
    
    st.markdown("---")

    # --- ส่วนกราฟ (Charts) ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("### 🍰 สัดส่วนรายจ่าย (แยกตามหมวดหมู่)")
        expense_df = df[df["Type"] == "รายจ่าย"]
        if not expense_df.empty:
            fig_pie = px.pie(expense_df, values='Amount', names='Category', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลรายจ่าย")

    with c2:
        st.write("### 📈 แนวโน้มรายรับ-รายจ่าย (ตามเวลา)")
        # แปลงวันที่ให้เป็น DateTime object เพื่อพล็อตได้ถูกต้อง
        df['Date'] = pd.to_datetime(df['Date'])
        df_grouped = df.groupby(['Date', 'Type'])['Amount'].sum().reset_index()
        
        if not df_grouped.empty:
            fig_bar = px.bar(df_grouped, x='Date', y='Amount', color='Type', barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูล")

    # --- ตารางข้อมูล ---
    st.subheader("📋 ประวัติรายการล่าสุด")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

else:
    st.info("ยังไม่มีข้อมูลในระบบ ลองกรอกข้อมูลทางเมนูด้านซ้ายดูสิครับ!")