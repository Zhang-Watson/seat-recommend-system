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

# 教室类别选择
classroom_type = st.sidebar.selectbox(
    "教室类别",
    [
    "第一类：标准型（代表：B21）",
    "第二类：陡峭型（代表：BX11）",
    "第三类：宽松/不对称型（代表：BX14）",
    "📌 其他类型（待测量添加）"
    ]
)

# 根据选择显示提示信息
if "标准型" in classroom_type:
    st.sidebar.success("✅ 适用教室：B11, B12, B21, B22, B31, B32, B41, B42, B51, B52")
    st.sidebar.info("💡 提示：同类型教室可参考本推荐方案")
elif "陡峭型" in classroom_type:
    st.sidebar.success("✅ 适用教室：BX11, BX12, BX21, BX22")
    st.sidebar.info("💡 提示：同类型教室可参考本推荐方案")
elif "宽松/不对称型" in classroom_type:
    st.sidebar.success("✅ 适用教室：BX13, BX14, BX23, BX24（BX14为不对称布局）")
    st.sidebar.info("💡 提示：同类型教室可参考本推荐方案")
else:
    st.sidebar.warning("🚧 该类型教室数据正在采集中")
    st.sidebar.info("📝 如需添加新教室，请提供以下参数：")
    st.sidebar.caption("• 黑板高h、黑板离地高b")
    st.sidebar.caption("• 首排距黑板距离d、排距q")
    st.sidebar.caption("• 地板倾角θ、总排数、总列数")
    st.sidebar.caption("• 布局是否对称（如不对称需说明分区排数）")

# 身高选项
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

st.sidebar.markdown("---")
st.sidebar.caption("基于视角模型 tanα 最大化 + 仰角 ≤30° 约束")

# ==================== 数据定义 ====================

# 第一类：标准型（以B21为代表）
standard_data = {
    "c1": [0.58, 0.65, 0.71, 0.76, 0.80, 0.82, 0.81, 0.78, 0.73, 0.67, 0.60, 0.52],
    "c2": [0.55, 0.62, 0.68, 0.73, 0.77, 0.79, 0.78, 0.75, 0.70, 0.64, 0.57, 0.49],
    "c3": [0.60, 0.67, 0.73, 0.78, 0.82, 0.84, 0.83, 0.80, 0.75, 0.69, 0.62, 0.54]
}

# 第二类：陡峭型（以BX11为代表）
steep_data = {
    "c1": [1.31, 1.00, 0.82, 0.70, 0.60, 0.54, 0.49, 0.44, 0.41, 0.38, 0.36],
    "c2": [1.25, 0.96, 0.79, 0.68, 0.58, 0.52, 0.47, 0.42, 0.39, 0.36, 0.34],
    "c3": [1.35, 1.04, 0.85, 0.73, 0.63, 0.57, 0.52, 0.47, 0.44, 0.41, 0.39]
}

# 第三类：宽松型（以BX14为代表）
loose_data = {
    "c1": [1.03, 0.79, 0.65, 0.55, 0.48, 0.43, 0.38, 0.35, 0.33, 0.30, 0.28, 0.26],
    "c2": [0.98, 0.76, 0.63, 0.53, 0.46, 0.41, 0.36, 0.33, 0.31, 0.28, 0.26, 0.24],
    "c3": [1.07, 0.82, 0.68, 0.58, 0.51, 0.46, 0.41, 0.38, 0.36, 0.33, 0.31, 0.29]
}

# 判断当前选择的教室类型
is_other_type = "其他" in classroom_type

if "标准型" in classroom_type:
    tanalpha_data = standard_data
    rows = 12
    cols = 15
    layout = "uniform"
    room_name = "标准型（B21为代表）"
    room_desc = "θ≈4°，排距0.75m，首排距3.60m"
    available = True
elif "陡峭型" in classroom_type:
    tanalpha_data = steep_data
    rows = 11
    cols = 28
    layout = "uniform"
    room_name = "陡峭型（BX11为代表）"
    room_desc = "θ≈15.5°，排距0.90m，首排距2.80m"
    available = True
elif "宽松/不对称型" in classroom_type:
    tanalpha_data = loose_data
    rows = 12
    cols = 16
    layout = "asymmetric"
    room_name = "宽松/不对称型（BX14为代表）"
    room_desc = "θ≈8.5°，排距1.00m，首排距2.80m | 右群仅8排"
    available = True
else:
    tanalpha_data = None
    rows = 10
    cols = 10
    layout = "uniform"
    room_name = "待添加教室"
    room_desc = "数据采集中，敬请期待"
    available = False

# 身高映射
if "较矮" in height_option:
    height_key = "c2"
elif "一般" in height_option:
    height_key = "c1"
else:
    height_key = "c3"

# ==================== 主界面 ====================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 座位推荐热力图")
    
    if not available:
        st.info("📝 **该类型教室数据正在采集中**")
        st.markdown("""
        ### 🔧 如何添加新教室？
        如需添加新的阶梯教室，请提供以下参数：
        - 黑板高度h、黑板离地高度b
        - 首排距黑板距离d、排距q
        - 地板倾角θ、总排数、总列数
        - 布局是否对称
        """)
        placeholder_matrix = np.zeros((rows, cols))
        df_placeholder = pd.DataFrame(placeholder_matrix)
        df_placeholder.index = [f"第{i+1}排" for i in range(rows)]
        df_placeholder.columns = [f"第{j+1}列" for j in range(cols)]
        st.dataframe(df_placeholder, height=450, use_container_width=True)
        st.caption("⬜ 待测量数据，暂无推荐")
    else:
        st.markdown("颜色越🟢**绿**越推荐，越🔴**红**越不推荐 | ⬜ **灰**表示无座位")
        
        current_tanalpha = tanalpha_data[height_key]
        score_matrix = np.zeros((rows, cols))
        
        if layout == "asymmetric":
            for row in range(rows):
                base_tanalpha = current_tanalpha[row]
                for col in range(cols):
                    if col >= 12 and row >= 8:
                        score_matrix[row][col] = -1
                        continue
                    center_offset = 1 - abs(col - cols/2) / (cols/2)
                    base_score = base_tanalpha * 10 * (0.7 + 0.3 * center_offset)
                    if "互动" in preference:
                        if row <= 2:
                            base_score += 1.5
                        elif row <= 4:
                            base_score += 0.5
                    if "视角" in preference:
                        if 3 <= row <= rows - 4:
                            base_score += 0.5
                    if height_key == "c2" and row > rows - 4:
                        base_score -= 1.0
                    if col < 2 or col > cols - 3:
                        base_score -= 1.0
                    score_matrix[row][col] = max(0, min(10, base_score))
        else:
            for row in range(rows):
                base_tanalpha = current_tanalpha[row]
                for col in range(cols):
                    center_offset = 1 - abs(col - cols/2) / (cols/2)
                    base_score = base_tanalpha * 10 * (0.7 + 0.3 * center_offset)
                    if "互动" in preference:
                        if row <= 2:
                            base_score += 1.5
                        elif row <= 4:
                            base_score += 0.5
                    if "视角" in preference:
                        if 3 <= row <= rows - 4:
                            base_score += 0.5
                    if height_key == "c2" and row > rows - 4:
                        base_score -= 1.0
                    if col < 2 or col > cols - 3:
                        base_score -= 1.0
                    score_matrix[row][col] = max(0, min(10, base_score))
        
        df_display = pd.DataFrame(score_matrix.round(1))
        df_display.index = [f"第{i+1}排" for i in range(rows)]
        df_display.columns = [f"第{j+1}列" for j in range(cols)]
        
        def color_score(val):
            if val == -1:
                return 'background-color: #D3D3D3; color: #888888'
            elif val >= 7:
                return 'background-color: #2D5A3F; color: #E0E0E0'
            elif val >= 4:
                return 'background-color: #5C4B2A; color: #E0E0E0'
            else:
                return 'background-color: #6B2E2E; color: #E0E0E0'
        
        styled_df = df_display.style.map(color_score).format("{:.1f}")
        st.dataframe(styled_df, height=450, use_container_width=True)
        
        st.markdown("""
        <div style="display: flex; gap: 20px; margin-top: 10px;">
            <div><span style="background-color: #2D5A3F; padding: 2px 10px; color: #E0E0E0;">🟢 7-10分</span> 强烈推荐</div>
            <div><span style="background-color: #5C4B2A; padding: 2px 10px; color: #E0E0E0;">🟡 4-6分</span> 一般</div>
            <div><span style="background-color: #6B2E2E; padding: 2px 10px; color: #E0E0E0;">🔴 0-3分</span> 不推荐</div>
            <div><span style="background-color: #D3D3D3; padding: 2px 10px; color: #888888;">⬜ 灰色</span> 无座位</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("💡 个性化推荐")
    
    if not available:
        st.info("📝 **数据采集中**")
        st.markdown("""
        本系统目前支持三类教室：
        - 标准型（B21等10间）
        - 陡峭型（BX11等4间）
        - 宽松/不对称型（BX14等4间）
        
        如有其他教室需求，请联系我们。
        """)
    else:
        st.markdown(f"**教室类别：** {room_name}")
        st.markdown(f"**特征：** {room_desc}")
        st.markdown(f"**你的身高：** {height_option.split('(')[0]}")
        st.markdown(f"**上课偏好：** {'互动优先' if '互动' in preference else '视角优先'}")
        st.markdown("---")
        
        if "标准型" in classroom_type:
            if "互动" in preference:
                st.success("✅ **推荐座位：第2-4排中间列**")
                st.info("📌 理由：便于与老师互动，板书清晰")
            else:
                st.success("✅ **推荐座位：第5-8排中间列**")
                st.info("📌 理由：视野饱满度最佳，仰角舒适")
            if height_key == "c2":
                st.warning("⚠️ 建议避免第10排以后")
        elif "陡峭型" in classroom_type:
            if "互动" in preference:
                st.success("✅ **推荐座位：第4-5排中间列**")
                st.info("📌 理由：陡峭教室前排仰角偏大，建议适度后移")
            else:
                st.success("✅ **推荐座位：第5-7排中间列**")
                st.info("📌 理由：仰角合格范围内，视野较舒适")
            st.warning("⚠️ 陡峭教室第1-3排仰角超标，不推荐")
        else:
            if "互动" in preference:
                st.success("✅ **推荐座位：第3-4排（左、中群）**")
                st.info("📌 理由：靠近老师，仰角可接受")
            else:
                st.success("✅ **推荐座位：第4-6排（左、中群）**")
                st.info("📌 理由：视野与舒适度平衡区域")
            st.info("📌 **注意：右侧群最后4列仅8排，第9-12排无座位**")
        
        st.markdown("---")
        st.caption("📐 基于实测数据 | 评分 = tanα × 10")

# 参数对比表
if available:
    st.markdown("---")
    st.subheader("📐 三类教室参数对比")
    param_data = {
        "参数": ["代表教室", "地板倾角θ", "排距q", "首排距d", "总排数", "典型布局"],
        "标准型": ["B21", "4°", "0.75m", "3.60m", "12排", "均匀对称"],
        "陡峭型": ["BX11", "15.5°", "0.90m", "2.80m", "11排", "均匀对称"],
        "宽松型": ["BX14", "8.5°", "1.00m", "2.80m", "12排", "右群不对称"]
    }
    df_params = pd.DataFrame(param_data)
    st.dataframe(df_params, use_container_width=True, hide_index=True)

st.markdown("---")

# ==================== 底部反馈邮箱 ====================
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #888888; border-top: 1px solid #444444; margin-top: 20px;">
    📬 意见建议请发送至邮箱：<strong>18357352108@163.com</strong>
</div>
""", unsafe_allow_html=True)

# 数学模型展开
with st.expander("📖 查看数学模型详情"):
    st.latex(r"\tan\alpha = \frac{\tan\beta - \tan\gamma}{1 + \tan\beta\tan\gamma}")
    st.latex(r"\tan\beta = \frac{b - c - (k-1)q\tan\theta + h}{x}")
    st.latex(r"\tan\gamma = \frac{b - c - (k-1)q\tan\theta}{x}")
    st.markdown("**参数说明：**")
    st.markdown("- α：视角 | β：仰角 | γ：俯角")
    st.markdown("- b：黑板离地高 | c：坐姿眼高 | h：黑板高 | q：排距 | θ：地板倾角 | x：水平距离")
