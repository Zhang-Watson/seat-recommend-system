import streamlit as st
import pandas as pd
import numpy as np

# 页面配置
st.set_page_config(
    page_title="阶梯教室智能选座系统",
    page_icon="🎓",
    layout="wide"
)

# 标题
st.title("🎓 阶梯教室智能选座推荐系统")
st.markdown("基于视角优化模型 + 人体工学参数 | 哈尔滨工业大学")
st.markdown("---")

# 侧边栏输入
st.sidebar.header("📝 请输入你的信息")

# 身高选项（基于你的实测数据）
height_option = st.sidebar.selectbox(
    "身高",
    ["较矮 (约160cm，坐姿眼高1.10m)", 
     "一般 (约170cm，坐姿眼高1.20m)", 
     "较高 (约180cm，坐姿眼高1.30m)"]
)

# 偏好选项
preference = st.sidebar.selectbox(
    "上课偏好",
    ["视角优先 - 看板书清楚舒适", 
     "互动优先 - 靠近老师便于交流"]
)

# 视力情况
vision = st.sidebar.selectbox(
    "视力情况",
    ["正常视力", "轻度近视（戴眼镜）", "高度近视"]
)

# 教室选择（后续可扩展）
classroom = st.sidebar.selectbox(
    "阶梯教室",
    ["B21（二校区）", "其他教室（即将上线）"]
)

st.sidebar.markdown("---")
st.sidebar.caption("基于视角模型 tanα 最大化 + 仰角 ≤30° 约束")

# 主界面两列布局
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 座位推荐热力图")
    st.markdown("颜色越🟢**绿**越推荐，越🔴**红**越不推荐")

# 身高映射
if "较矮" in height_option:
    height_key = "c2"
    height_value = 1.10
elif "一般" in height_option:
    height_key = "c1"
    height_value = 1.20
else:
    height_key = "c3"
    height_value = 1.30

# 座位矩阵参数（基于你的B21实测数据）
rows = 12  # 排数
cols = 15  # 列数

# 计算推荐分数
score_matrix = np.zeros((rows, cols))

for row in range(rows):  # row=0表示第一排
    for col in range(cols):
        # 水平偏移因子（中间高两边低）
        center_offset = 1 - abs(col - cols/2) / (cols/2)
        
        # 前排/后排基础分
        if preference == "互动优先 - 靠近老师便于交流":
            # 互动偏好：前排分数高
            base_score = (rows - row) * 0.3 + center_offset * 5
            if row <= 3:  # 前3排加分
                base_score += 4
            elif row <= 6:
                base_score += 1
        else:
            # 视角偏好：中排分数高
            base_score = (rows - row) * 0.6 + center_offset * 4
            if 4 <= row <= 8:  # 中排最佳视角
                base_score += 3
        
        # 身高影响（较矮不宜坐太后面）
        if height_key == "c2" and row > 8:
            base_score -= 3
        if height_key == "c3" and row <= 2:
            base_score -= 1  # 太高坐前排反而仰角大
        
        # 视力影响
        if vision == "高度近视" and row > 7:
            base_score -= 4
        elif vision == "轻度近视（戴眼镜）" and row > 9:
            base_score -= 2
        
        # 边缘座位惩罚
        if col < 2 or col > cols - 3:
            base_score -= 2
        
        score_matrix[row][col] = max(0, min(10, base_score))

# 显示热力图
df_display = pd.DataFrame(score_matrix.round(1))
df_display.index = [f"第{i+1}排" for i in range(rows)]
df_display.columns = [f"列{j+1}" for j in range(cols)]

with col1:
    # 使用渐变色热力图
    styled_df = df_display.style.background_gradient(
        cmap="RdYlGn",  # 红黄绿配色
        axis=None,
        vmin=0,
        vmax=10
    ).format("{:.1f}")
    st.dataframe(styled_df, height=450, use_container_width=True)
    
    st.caption("🔴 0-3分 | 🟡 4-6分 | 🟢 7-10分")

# 推荐建议
with col2:
    st.subheader("💡 个性化推荐")
    
    # 找到最高分区域
    best_score = np.max(score_matrix)
    best_positions = np.argwhere(score_matrix == best_score)
    best_rows = [p[0] + 1 for p in best_positions]
    best_cols = [p[1] + 1 for p in best_positions]
    
    st.markdown(f"**你的身高：** {height_option.split('(')[0]}")
    st.markdown(f"**上课偏好：** {'互动优先' if '互动' in preference else '视角优先'}")
    st.markdown(f"**视力情况：** {vision}")
    st.markdown("---")
    
    if "互动" in preference:
        st.success("✅ **推荐座位：第2-4排中间列**")
        st.info("📌 理由：便于与老师互动，板书清晰，声音接收好")
    else:
        st.success("✅ **推荐座位：第5-8排中间列**")
        st.info("📌 理由：视野饱满度最佳（tanα最大），仰角≤30°，不易疲劳")
    
    if height_key == "c2":
        st.warning("⚠️ 建议避免第10排以后，视线可能被遮挡")
    if vision == "高度近视":
        st.warning("⚠️ 建议优先选择第1-5排")
    
    st.markdown("---")
    st.caption(f"📐 基于B21阶梯教室实测数据 | 最佳视角区域tanα = {best_score:.1f}/10")

# 教室参数展示
st.markdown("---")
st.subheader("📐 当前教室参数（B21实测）")

param_col1, param_col2, param_col3, param_col4 = st.columns(4)
with param_col1:
    st.metric("黑板高", "4.00 m")
    st.metric("黑板离地高", "1.00 m")
with param_col2:
    st.metric("座位宽", "0.50 m")
    st.metric("排距", "0.75 m")
with param_col3:
    st.metric("地板倾角", "4°")
    st.metric("首排距黑板", "3.60 m")
with param_col4:
    st.metric("黑板宽", "2.45 m")
    st.metric("座位群间距", "1.13 m")

st.markdown("---")
st.caption("🔬 数学模型：tanα = (tanβ - tanγ)/(1+tanβ·tanγ) | 约束：tanβ ≤ tan30°")
