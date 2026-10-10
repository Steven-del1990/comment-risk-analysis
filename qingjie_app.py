# 导入需要用到的工具库
import streamlit as st
import pandas as pd

# 页面基础设置：必须放在最开头
st.set_page_config(
    page_title="清界-网暴审核系统",
    layout="wide"
)

# 页面大标题
st.title("清界：网络暴力评论风险审核原型")
# 灰色副标题
st.caption("面向网络平台人工审核人员的网络暴力风险研判辅助工具")
# 左侧侧边栏
with st.sidebar:
    st.header("操作面板")
    st.write("请上传评论数据CSV文件")
# 上传CSV按钮
uploaded_file = st.file_uploader(
    label="上传评论CSV",
    type=["csv"],
    help="CSV必须包含列：content(评论文本)、like_num(点赞数)、reply_num(回复数)、time(发布时间)"
)
# 用户上传文件后才执行下面逻辑
if uploaded_file is not None:
    # 用pandas读取CSV，转成表格对象
    df = pd.read_csv(uploaded_file)
    
    # 页面展示原始表格
    st.subheader("📊 原始评论数据")
    st.dataframe(df, use_container_width=True)
    # 检查CSV是否有time列，有才画图
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
        # 按小时分组，统计评论、回复、点赞
        agg_by_hour = df.groupby(df["time"].dt.hour).agg(
            评论数量=("content", "count"),
            总回复数=("reply_num", "sum"),
            总点赞数=("like_num", "sum")
        )
        # 构造综合热度，回复权重高于点赞，可在论文说明权重设计
        agg_by_hour["综合传播热度"] = agg_by_hour["评论数量"] + agg_by_hour["总回复数"] * 0.6 + agg_by_hour["总点赞数"] * 0.2

        st.subheader("📈 评论传播趋势（按小时：综合传播热度）")
        st.line_chart(agg_by_hour["综合传播热度"])

    # 导出按钮
    st.subheader("💾 导出审核结果")
    st.download_button(
        label="📥 下载带风险标签的CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="审核结果.csv",
        mime="text/csv"
    )

