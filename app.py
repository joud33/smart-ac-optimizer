import streamlit as st
import pandas as pd
import numpy as np

# ==========================
# إعداد الصفحة
# ==========================
st.set_page_config(page_title="محسّن الطاقة الذكي", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"]  { direction: rtl; text-align: right; font-family: Arial; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ محسّن الطاقة الذكي للمباني")
st.caption("نظام ذكاء اصطناعي لتحليل استهلاك الطاقة واختيار أفضل إعدادات لتقليل التكلفة وزيادة الكفاءة.")

# ==========================
# الشريط الجانبي
# ==========================
st.sidebar.header("⚙️ بيانات المبنى")

area = st.sidebar.slider("مساحة المبنى (م²)", 50, 5000, 1000)
people = st.sidebar.slider("عدد الأشخاص", 0, 300, 50)
outside_temp = st.sidebar.slider("درجة الحرارة الخارجية (°م)", 10, 50, 38)
indoor_temp = st.sidebar.slider("درجة الحرارة الحالية داخل المبنى (°م)", 16, 35, 27)
humidity = st.sidebar.slider("نسبة الرطوبة (%)", 20, 90, 60)

st.sidebar.divider()

hvac_hours = st.sidebar.slider("ساعات تشغيل التكييف", 0, 24, 10)
lighting_hours = st.sidebar.slider("ساعات تشغيل الإضاءة", 0, 24, 10)
device_level = st.sidebar.slider("مستوى تشغيل الأجهزة", 0.0, 1.0, 0.5)

electricity_price = st.sidebar.number_input("سعر الكيلوواط (ريال)", 0.0, 5.0, 0.18)

# ==========================
# دوال الحساب
# ==========================
def comfort_score(setpoint):
    ideal = 24
    score = 100 - abs(setpoint - ideal) * 10 - (humidity - 50) * 0.5
    return max(0, min(100, score))

def energy_model(setpoint):
    delta = max(0, outside_temp - setpoint)
    hvac = area * 0.012 * delta * hvac_hours * (1 + people/200)
    lighting = area * 0.01 * lighting_hours
    devices = area * 0.008 * device_level * 10
    total = hvac + lighting + devices
    return total, hvac, lighting, devices

# ==========================
# اختيار أفضل درجة تلقائيًا
# ==========================
results = []

for sp in range(20, 29):
    total, hvac, light, dev = energy_model(sp)
    comfort = comfort_score(sp)
    score = comfort * 1.2 - total * 0.1
    results.append([sp, total, hvac, light, dev, comfort, score])

df = pd.DataFrame(results, columns=[
    "درجة الضبط", "إجمالي الاستهلاك", "التكييف",
    "الإضاءة", "الأجهزة", "الراحة", "التقييم"
])

best = df.sort_values("التقييم", ascending=False).iloc[0]

# ==========================
# عرض النتائج
# ==========================
st.subheader("📊 النتائج الذكية")

col1, col2, col3 = st.columns(3)

col1.metric("أفضل درجة ضبط", f"{int(best['درجة الضبط'])}°م")
col2.metric("الاستهلاك المتوقع", f"{best['إجمالي الاستهلاك']:.1f} kWh")
col3.metric("مؤشر الراحة", f"{best['الراحة']:.0f}/100")

cost = best["إجمالي الاستهلاك"] * electricity_price
st.metric("💰 التكلفة اليومية المتوقعة", f"{cost:.2f} ريال")

st.divider()

st.subheader("📈 مقارنة جميع الخيارات")
st.dataframe(df.drop(columns=["التقييم"]))

st.divider()

st.subheader("🧠 التوصيات الذكية")

if best["الراحة"] < 70:
    st.warning("الراحة منخفضة — يُنصح بضبط التكييف أو تقليل عدد الأشخاص.")
elif best["إجمالي الاستهلاك"] > 300:
    st.warning("الاستهلاك مرتفع — يُنصح بتقليل ساعات التشغيل أو تحسين العزل.")
else:
    st.success("الوضع الحالي متوازن بين الكفاءة والراحة.")

st.info("خفض درجة واحدة في التكييف قد يوفر حتى 5% من استهلاك الطاقة تقريبًا.")
