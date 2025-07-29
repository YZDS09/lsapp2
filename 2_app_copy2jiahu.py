import os
import time
from io import StringIO
from io import BytesIO  # 导入内存文件流模块

import streamlit as st
import pandas as pd
# 在文件顶部添加导入
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_echarts import st_echarts


# =======预设图表配置==========================
CHART_CONFIG = {
    # 1.对外贸易指标组
    "进出口总额及分项（出口 / 进口）对比图": {
        "type": "line",
        "columns": ["进出口总额", "出口总额", "进口总额"],
        "x_axis": "指标名称"
    },
    "高新技术产品出口与工业增加值的相关性": {
        "type": "scatter",
        "columns": ["  其中：高新技术产品"],            # 数值列
        "x_axis": "  其中：工业增加值"            # 分类列
    },
    "高新技术出口占比": {
        "type": "pie",
        "x_axis": "进出口总额",  # 总额列名
        "columns": ["  其中：高新技术产品"]  # 部分金额列名列表
    },
    # 2.外商投资指标组
    "外资：合同金额/实际使用的时间趋势": {
        "type": "line",
        "columns": ["实际使用外资金额","合同外资金额"],      
        "x_axis": "指标名称"            
    },
    "外资：合同金额/实际使用对比图": {
        "type": "grouped_bar",
        "columns": ["合同外资金额", "实际使用外资金额"],  # 每组一个柱子
        "line_columns": ["合同外资金额"],
        "x_axis": "指标名称",
        "group_names": ["合同外资金额", "实际使用外资金额"],
        "line_name": "增长率趋势",
        "line_color": "#FFA500",
        "bar_colors": ["#1f77b4", "#ff7f0e"]
    },
    "历年累计实际使用外资金额": {
        "type": "bar",
        "columns": ["实际使用外资金额"],  # 需要展示的数值列
        "x_axis": "指标名称"                     # X轴列名
    },
    "大企业在新增企业中的比例": {
        "type": "pie",
        "x_axis": "新增外商投资企业数",  # 总额列名
        "columns": ["  其中：投资额1000万美元及以上的企业数"]  # 部分金额列名列表
    },
    # 3. 经济产出指标组
    "地区生产总值及二三产业增加值趋势图": {
        "type": "line",
        "columns": ["地区生产总值", "  其中：第二产业增加值", "        第三产业增加值 "],      
        "x_axis": "指标名称"            
    },
    "第二三产业GDP占比趋势图": {
        "type": "pie",
        "x_axis": "地区生产总值",  # 总额列名
        "columns": ["  其中：第二产业增加值", "        第三产业增加值 "]  # 部分金额列名列表
    },
    "工业增加值 vs 能源消费量": {
        "type": "scatter",
        "columns": ["  其中：工业增加值"],            # 数值列
        "x_axis": "规模以上工业法人单位综合能源消费量"            # 分类列
    },
    # 4. 企业绩效指标组
    "‘四上’企业分行业营业收入对比图": {
        "type": "bar",
        "columns": ["  其中：规模以上工业法人单位", "        有资质的建筑业企业", "        限额以上批零住餐企业","        房地产开发经营业企业","        规模以上服务业企业"],
        "x_axis": "指标名称"
    },
    "各行业收入/工业总产值趋势图": {
        "type": "line",
        "columns": ["  其中：规模以上工业法人单位", "        有资质的建筑业企业", "        限额以上批零住餐企业","        房地产开发经营业企业","        规模以上服务业企业","规模以上工业总产值"],      
        "x_axis": "指标名称"            
    },
    "行业相关性热力图": {
        "type": "correlation_heatmap",
        "x_axis": "地区生产总值",  # 时间列
        "columns": ["  其中：规模以上工业法人单位", "        有资质的建筑业企业", "        限额以上批零住餐企业","        房地产开发经营业企业","        规模以上服务业企业","规模以上工业总产值"],  # 需要展示的两个指标
        #"color_scale": "Viridis"  # 颜色方案
    },
    "外商投资/高新技术企业在总营业收入中的比例": {
        "type": "pie",
        "x_axis": "“四上”企业营业收入",  # 总额列名
        "columns": ["  其中：外商投资企业", "  其中：高新技术企业"]  # 部分金额列名列表
    },
    #5. 投资与基础设施指标组
    "固定资产投资及基础设施投资趋势图": {
        "type": "line",
        "columns": ["固定资产投资（不含农户）", "  其中：基础设施投资"],      
        "x_axis": "指标名称"            
    },
    "基础设施投资在固定资产投资中的比例": {
        "type": "pie",
        "x_axis": "固定资产投资（不含农户）",  # 总额列名
        "columns": ["  其中：基础设施投资"]  # 部分金额列名列表
    },
    "固定资产投资 vs GDP": {
        "type": "dual_axis_line",
        "columns": ["固定资产投资（不含农户）"],   # 左侧Y轴的数据列
        "right_columns": ["地区生产总值"],  # 右侧Y轴的数据列
        "x_axis": "指标名称",              # X轴列名
        "left_title": "固定资产投资（不含农户）",    # 左侧Y轴标题
        "right_title": "地区生产总值"         # 右侧Y轴标题
    },
    # 6. 就业指标组
    "“四上”企业从业人数趋势图": {
        "type": "line",
        "columns": ["“四上”企业从业人员期末人数"],      
        "x_axis": "指标名称"            
    },
    # 7. 能源与环境指标组
    "各行业收入/工业总产值趋势图": {
        "type": "line",
        "columns": ["  其中：规模以上工业法人单位", "        有资质的建筑业企业", "        限额以上批零住餐企业","        房地产开发经营业企业","        规模以上服务业企业","规模以上工业总产值"],      
        "x_axis": "指标名称"            
    },
    "能源消费 vs 工业总产值": {
        "type": "scatter",
        "columns": ["规模以上工业总产值"],            # 数值列
        "x_axis": "规模以上工业法人单位综合能源消费量"            # 分类列
    },

    # 8. 财政指标组
    "税收增长趋势图": {
        "type": "line",
        "columns": ["税收收入"],      
        "x_axis": "指标名称"            
    },
    "税收收入 vs GDP": {
        "type": "scatter",
        "columns": ["税收收入"],            # 数值列
        "x_axis": "地区生产总值"            # 分类列
    },
    # 9. 企业数量指标组
    "新增/期末企业数趋势对比": {
        "type": "line",
        "columns": ["新增内资企业数","期末实有企业" ],      
        "x_axis": "指标名称"            
    },
    "期末实有企业中高新技术、上市、“四上”企业的占比": {
        "type": "pie",
        "x_axis": "期末实有企业",  # 总额列名
        "columns": ["  其中：高新技术企业","  其中：上市企业","  其中：“四上”企业"]  # 部分金额列名列表
    },
    # 10. 创新指标组
    "研发机构数和专利授权量": {
        "type": "line",
        "columns": ["期末研发机构数", "期末研发机构数"],
        "x_axis": "指标名称"
    },
    "固定资产投资（不含农户）规模图": {
        "type": "bar",
        "columns": ["固定资产投资（不含农户）"],
        "x_axis": "指标名称"
    },
    "发明专利占比": {
        "type": "pie",
        "x_axis": "当年专利授权量",  # 总额列名
        "columns": ["  其中：发明专利"]  # 部分金额列名列表
    },
    "专利授权量 vs 高新技术企业数": {
        "type": "scatter",
        "columns": ["当年专利授权量"],            # 数值列
        "x_axis": "  其中：高新技术企业"            # 分类列
    },
}

# 初始化全局状态
class GlobalState:
    def __init__(self):
        self.raw_df = None      # 存储原始数据（DataFrame）
        self.cleaned_df = None      # 存储清洗后的数据
        self.current_page = "数据导入"      # 当前页面标识符(默认 数据导入)
        self.file_uploaded = False      ## 文件上传状态标记

    #一键重置所有数据相关的状态，保持状态一致性。
    def reset_data(self):
        self.raw_df = None
        self.cleaned_df = None
        self.file_uploaded = False

# 创建全局状态
def init_global_state():
    if 'global_state' not in st.session_state:
        st.session_state.global_state = GlobalState()
    return st.session_state.global_state

# 工具函数模块
class DataUtils:
    @staticmethod
    def load_data(uploaded_file):
        """判断格式选取读法"""
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            # 创建布尔掩码，标记需要删除的行
            mask = (df.iloc[:, 0] == '计量单位') | (df.iloc[:, 0] == '代码')

            # 保留掩码为False的行（即不是"号码"或"类型"的行）
            df = df[~mask]
            df['指标名称'] = pd.to_numeric(df['指标名称'], errors='coerce')  # 先转换为数值类型
            df['指标名称'] = pd.to_datetime(df['指标名称'],unit='M', origin='1899-12-30',errors='coerce')
            df['指标名称'] = df['指标名称'].interpolate(method='linear')
            df['指标名称'] = df['指标名称'].dt.to_period('M')  # 只保留月份
            df['指标名称'] = df['指标名称'].astype(str)
            #df['指标名称'] = df['指标名称'].dt.to_period('Y')  # 只保留月份
            return df
        
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, parse_dates=[0])
            # 创建布尔掩码，标记需要删除的行
            mask = (df.iloc[:, 0] == '计量单位') | (df.iloc[:, 0] == '代码')

            # 保留掩码为False的行（即不是"号码"或"类型"的行）
            df = df[~mask]
            df['指标名称'] = pd.to_numeric(df['指标名称'], errors='coerce')  # 先转换为数值类型
            df['指标名称'] = pd.to_datetime(df['指标名称'],unit='D', origin='1899-12-30',errors='coerce')
            df['指标名称'] = df['指标名称'].interpolate(method='linear')
            df['指标名称'] = df['指标名称'].dt.to_period('M')  # 只保留月份
            df['指标名称'] = df['指标名称'].astype(str)
            #df['指标名称'] = df['指标名称'].dt.to_period('Y')  # 只保留月份
            return df
        
        else:
            st.error("不支持的文件格式")
            return None

    @staticmethod
    def get_data_summary(df):
        """获取数据集的摘要信息"""
        if df is None:
            return {}
        
        summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
        return summary

# 数据导入模块
class DataImportModule:
    def __init__(self, state):
        self.state = state
    
    def render(self):
        st.header("📤 数据导入")
        
        # 文件上传区域
        uploaded_file = st.file_uploader(
           "上传数据文件(CSV/Excel)",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=False,
            key="file_uploader"     #组件的唯一标识符，踪该组件的状态
        )
        
        # 上传文件处理
        if uploaded_file:
            with st.spinner("正在加载数据..."):
                df = DataUtils.load_data(uploaded_file)
                self.state.raw_df = df
            
            if self.state.raw_df is not None:
                self.state.file_uploaded = True
                st.success(f"数据导入成功! 文件名: {uploaded_file.name}")
                # 显示数据摘要
                self._display_data_summary(self.state.raw_df)
                
                # 显示数据预览
                self._display_data_preview(self.state.raw_df)
    
    def _display_data_summary(self, df):
        """显示数据摘要信息"""
        summary = DataUtils.get_data_summary(df)
        
        st.subheader("数据概述")

        # 创建容器包裹特定expander
        container = st.container()
        with container:
            # 添加只针对这个容器的CSS
            with st.expander("", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总行数", summary["shape"][0])
                with col2:
                    st.metric("总列数", summary["shape"][1])
                with col3:
                    missing_total = sum(summary["missing_values"].values())
                    st.metric("缺失值总数", missing_total)
            
                st.write("**列信息:**")
                st.write(list(df.columns))
    
    def _display_data_preview(self, df):
        """显示数据预览"""
        st.subheader("数据预览")
        st.dataframe(df, height=400, use_container_width=True)

# 数据清洗模块
class DataCleaningModule:
    def __init__(self, state):
        self.state = state
        self.cleaning_options = {
            "删除包含空值的行": self.handle_missing_values,
            "删除重复值": self.handle_duplicates,
            #"删除指定列": self.handle_drop_columns,
            "删除指定行": self.handle_drop_rows,
            #"数据格式化": self.handle_data_formatting,
            "缺失值填充": self.handle_missing_value_imputation
        }
    
    def render(self):
        st.header("🧹 数据清洗")
        
        if not self.state.file_uploaded or self.state.raw_df is None:
            st.warning("请先在数据导入页面上传数据")
            return
        
        # 显示原始数据摘要
        self._display_data_summary(self.state.raw_df, "原始数据")
        
        # 初始化清洗后的数据
        if self.state.cleaned_df is None:
            self.state.cleaned_df = self.state.raw_df.copy()
        
        # 清洗选项
        st.divider()
        st.subheader("清洗操作")
        selected_options = st.multiselect(
            "请选择具体操作",
            options=list(self.cleaning_options.keys()),
            key="cleaning_options"
        )
        
        # 应用清洗操作
        for option in selected_options:
            self.cleaning_options[option]()
        
        #显示清洗结果
        #self._display_data_summary(self.state.cleaned_df, "清洗后数据")
  
        # 数据导出
        st.divider()
        self._render_export_section()
    
    def _display_data_summary(self, df, title):
        # """显示数据摘要"""
        # with st.expander(f"{title}摘要"):
        #     st.write(f"**形状:** {df.shape[0]}行 × {df.shape[1]}列")
            
        #     # 列信息
        #     st.write("**列信息:**")
        #     col_info = pd.DataFrame({
        #         "列名": df.columns,
        #         "类型": df.dtypes,
        #         "缺失值": df.isnull().sum().values
        #     })
        #     st.dataframe(col_info, hide_index=True)

        # 显示当前数据的前几行以便用户参考
        st.write("当前数据预览:")
        st.dataframe(self.state.cleaned_df, height=400)
    
    def handle_missing_values(self):
        """处理缺失值"""
        initial_count = len(self.state.cleaned_df)
        self.state.cleaned_df = self.state.cleaned_df.dropna()
        removed_count = initial_count - len(self.state.cleaned_df)
        st.success(f"删除了 {removed_count} 行包含空值的记录")

    def handle_duplicates(self):
        """处理重复值"""
        initial_count = len(self.state.cleaned_df)
        self.state.cleaned_df = self.state.cleaned_df.drop_duplicates()
        removed_count = initial_count - len(self.state.cleaned_df)
        st.success(f"删除了 {removed_count} 条重复记录")

    # 待开发
    # def handle_drop_columns(self):
    #     """删除指定列"""
    #     st.subheader("删除指定列")
    #     cols_to_drop = st.multiselect(
    #         "选择要删除的列",
    #         options=self.state.cleaned_df.columns,
    #         key="columns_to_drop"
    #     )
    #     if cols_to_drop:
    #         self.state.cleaned_df = self.state.cleaned_df.drop(columns=cols_to_drop)
    #         st.success(f"已删除列: {', '.join(cols_to_drop)}")

#========================================================================
    def handle_drop_rows(self):
        """删除指定行"""
        st.subheader("删除指定行")
        
        # 获取用户输入的行号
        row_input = st.text_input(
            "输入要删除的行号（逗号分隔，支持范围如1-5）",
            placeholder="例如: 1,3,5-8,10",
            key="rows_to_drop"
        )
        
        if row_input:
            try:
                # 解析用户输入的行号
                rows_to_drop = self._parse_row_input(row_input, len(self.state.cleaned_df))
                
                if rows_to_drop:
                    # 保存原始行数用于统计
                    initial_count = len(self.state.cleaned_df)
                    
                    # 删除指定行
                    self.state.cleaned_df = self.state.cleaned_df.drop(rows_to_drop)
                    
                    # 重置索引
                    self.state.cleaned_df.reset_index(drop=True, inplace=True)
                    
                    # 显示操作结果
                    removed_count = initial_count - len(self.state.cleaned_df)
                    st.success(f"已删除 {removed_count} 行数据")
                    
                    # # 显示删除后的数据预览
                    # st.write("删除后数据预览:")
                    # st.dataframe(self.state.cleaned_df, height=200)
                    # print(self.state.cleaned_df)
                else:
                    st.warning("未找到有效的行号，请检查输入格式")
            except Exception as e:
                st.error(f"处理行号时出错: {str(e)}")
    
    def _parse_row_input(self, input_str, max_row):
        """解析用户输入的行号"""
        rows_to_drop = set()
        
        # 按逗号分割不同的行号范围
        parts = input_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                # 处理范围 (如 1-5)
                range_parts = part.split('-')
                if len(range_parts) == 2:
                    try:
                        start = int(range_parts[0].strip())
                        end = int(range_parts[1].strip())
                        if 0 <= start <= end < max_row:
                            rows_to_drop.update(range(start, end + 1))
                    except ValueError:
                        continue
            else:
                # 处理单个行号
                try:
                    row_num = int(part.strip())
                    if 0 <= row_num < max_row:
                        rows_to_drop.add(row_num)
                except ValueError:
                    continue
        
        return list(rows_to_drop)

    def handle_data_formatting(self):
        """数据格式化：第一列转时间，其余列转数值型"""
        st.subheader("数据格式化")
        
        if self.state.cleaned_df is None or self.state.cleaned_df.empty:
            st.warning("没有可格式化的数据")
            return
            
        # 显示当前数据类型
        st.write("当前数据类型:")
        dtype_info = pd.DataFrame({
            "列名": self.state.cleaned_df.columns,
            "当前类型": self.state.cleaned_df.dtypes.astype(str)
        })
        st.dataframe(dtype_info, hide_index=True)
        
        # 添加Excel日期序列号转换选项
        st.info("如果第一列包含Excel日期序列号（如44682、44713等），请勾选下方选项")
        is_excel_dates = st.checkbox("第一列是Excel日期序列号")
        
        # 执行格式化操作
        if st.button("执行格式化"):
            try:
                # 创建原始数据的副本用于比较
                original_df = self.state.cleaned_df.copy()
                
                # 转换第一列为时间类型
                first_col = self.state.cleaned_df.columns[0]
                
                if is_excel_dates:
                    # 处理Excel日期序列号
                    # Excel日期是从1900-01-01开始的天数
                    # 使用origin='1899-12-30'来校正Excel的日期偏移错误
                    self.state.cleaned_df[first_col] = pd.to_datetime(
                        self.state.cleaned_df[first_col].astype(float), 
                        unit='D', 
                        origin='1899-12-30',
                        errors='coerce'
                    )
                else:
                    # 常规时间转换
                    self.state.cleaned_df[first_col] = pd.to_datetime(
                        self.state.cleaned_df[first_col], 
                        errors='coerce'
                    )
                
                # 转换其余列为数值型
                other_cols = self.state.cleaned_df.columns[1:]
                for col in other_cols:
                    self.state.cleaned_df[col] = pd.to_numeric(
                        self.state.cleaned_df[col], 
                        errors='coerce'
                    )
                
                # 显示格式化结果
                st.success("数据格式化完成！")
                
                # 显示转换前后的数据类型对比
                st.write("数据类型变化:")
                dtype_changes = pd.DataFrame({
                    "列名": self.state.cleaned_df.columns,
                    "原始类型": original_df.dtypes.astype(str),
                    "新类型": self.state.cleaned_df.dtypes.astype(str)
                })
                st.dataframe(dtype_changes, hide_index=True)
                
                # 显示转换失败的统计
                failed_conversions = {}
                for col in self.state.cleaned_df.columns:
                    na_count = self.state.cleaned_df[col].isna().sum()
                    original_na = original_df[col].isna().sum()
                    failed_conversions[col] = na_count - original_na
                
                if any(failed_conversions.values()):
                    st.warning("部分数据转换失败:")
                    for col, count in failed_conversions.items():
                        if count > 0:
                            st.write(f"- **{col}**: {count} 个值无法转换，已被设为NaN")
                
                # 显示格式化后的数据预览
                st.write("格式化后数据预览:")
                
                # 创建格式化后的预览数据（时间列格式化为年月）
                preview_df = self.state.cleaned_df.copy()
                
                # 如果第一列是日期类型，格式化为年月
                if pd.api.types.is_datetime64_any_dtype(preview_df[first_col]):
                    preview_df[first_col] = preview_df[first_col].dt.strftime('%Y年%m月')
                
                st.dataframe(preview_df.head(), height=200)
                
                # 添加日期范围信息
                if pd.api.types.is_datetime64_any_dtype(self.state.cleaned_df[first_col]):
                    min_date = self.state.cleaned_df[first_col].min()
                    max_date = self.state.cleaned_df[first_col].max()
                    st.info(f"时间范围: {min_date.strftime('%Y年%m月')} 至 {max_date.strftime('%Y年%m月')}")
                
            except Exception as e:
                st.error(f"格式化过程中出错: {str(e)}")

    def handle_missing_value_imputation(self):
        """缺失值填充：时间列按时间填充，数值列用均值填充"""
        st.subheader("缺失值填充")
        
        if self.state.cleaned_df is None or self.state.cleaned_df.empty:
            st.warning("没有可填充的数据")
            return
            
        # 显示缺失值统计
        missing_counts = self.state.cleaned_df.isnull().sum()
        missing_cols = missing_counts[missing_counts > 0]
        
        if missing_cols.empty:
            st.success("数据中没有缺失值，无需填充")
            return
            
        st.write("各列缺失值数量:")
        missing_df = pd.DataFrame({
            "列名": missing_cols.index,
            "缺失值数量": missing_cols.values
        })
        st.dataframe(missing_df, hide_index=True)
        
        # 执行填充操作
        if st.button("执行填充"):
            try:
                # 创建填充前的数据副本用于比较
                original_df = self.state.cleaned_df.copy()
     
                # 填充其他列
                for col in self.state.cleaned_df.columns:

                    # 数值列使用均值填充
                    if pd.api.types.is_numeric_dtype(self.state.cleaned_df[col]):
                        mean_val = self.state.cleaned_df[col].mean()
                        self.state.cleaned_df[col] = self.state.cleaned_df[col].fillna(mean_val)
                    # 其他类型使用众数填充
                    else:
                        mode_val = self.state.cleaned_df[col].mode()[0] if not self.state.cleaned_df[col].mode().empty else None
                        if mode_val is not None:
                            self.state.cleaned_df[col] = self.state.cleaned_df[col].fillna(mode_val)
                
                # 显示填充结果
                st.success("缺失值填充完成！")
                
                # 显示填充前后的缺失值对比
                original_missing = original_df.isnull().sum().sum()
                new_missing = self.state.cleaned_df.isnull().sum().sum()
                filled_count = original_missing - new_missing
                
                st.info(f"共填充了 {filled_count} 个缺失值")
                st.write("填充后缺失值统计:")
                st.dataframe(self.state.cleaned_df.isnull().sum().to_frame("缺失值数量").T)
                
                # 显示填充后的数据预览
                st.write("填充后数据预览:")
                st.dataframe(self.state.cleaned_df, height=200)
                
            except Exception as e:
                st.error(f"填充过程中出错: {str(e)}")
#  ==============================================================      

    
    def _render_export_section(self):
        """渲染数据导出部分"""
        st.subheader("数据导出")
        
        if self.state.cleaned_df is not None:
            # 导出选项
            export_format = st.radio("导出格式", ["CSV", "Excel"], horizontal=True)
            
            if export_format == "CSV":
                file_name = st.text_input("文件名", "cleaned_data.csv")
                csv = self.state.cleaned_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="下载CSV文件",
                    data=csv,
                    file_name=file_name,
                    mime='text/csv'
                )
            else:
                file_name = st.text_input("文件名", "cleaned_data.xlsx")
                # 创建内存文件流
                output = BytesIO()
                # 将数据写入内存流（而非直接返回）
                self.state.cleaned_df.to_excel(output, index=False, engine='openpyxl')
                # 将文件指针移到开头（否则下载的文件会为空）
                output.seek(0)

                st.download_button(
                    label="下载Excel文件",
                    data=output,
                    file_name=file_name,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

# 数据看板模块
class DashboardModule:
    def __init__(self, state):
        self.state = state
        # 预设图表配置
        self.CHART_CONFIG = CHART_CONFIG
    
    def render(self):
        st.header("📊 数据看板")
        
        if not self.state.file_uploaded or self.state.raw_df is None:
            st.warning("请先在数据导入页面上传数据")
            return
        
        # 选择数据源
        data_source = st.radio(
            "选择数据源",
            ["原始数据", "清洗后数据"],
            horizontal=True,
            index=1 if self.state.cleaned_df is not None else 0
        )
        
        df = self.state.cleaned_df if data_source == "清洗后数据" and self.state.cleaned_df is not None else self.state.raw_df
        
        # 显示数据摘要
        st.subheader("数据摘要")
        self._display_data_summary(df)
        
        # 新增：预设图表展示
        st.divider()
        self._render_preset_charts(df)
    
    def _display_data_summary(self, df):
        """显示数据摘要"""
        summary = DataUtils.get_data_summary(df)
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("总行数", summary["shape"][0])
        with cols[1]:
            st.metric("总列数", summary["shape"][1])
        with cols[2]:
            missing_total = sum(summary["missing_values"].values())
            st.metric("缺失值", missing_total)
        with cols[3]:
            duplicates = df.duplicated().sum()
            st.metric("重复值", duplicates)
        
        # # 数据类型分布
        # with st.expander("数据类型分布"):
        #     dtypes_count = df.dtypes.value_counts().reset_index()
        #     dtypes_count.columns = ['数据类型', '数量']
        #     st.bar_chart(dtypes_count.set_index('数据类型'))
            
    def _render_preset_charts(self, df):
        """渲染预设图表展示功能"""
        st.subheader("预设图表展示")
        
        # 1. 筛选有效的图表配置
        valid_charts = {}
        missing_charts = []
        
        for chart_name, config in self.CHART_CONFIG.items():
            required_cols = [config["x_axis"]] + config["columns"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if not missing_cols:
                valid_charts[chart_name] = config
            else:
                missing_charts.append((chart_name, missing_cols))
        
        # 2. 显示缺失图表的警告信息
        if missing_charts:
            warning_msg = "以下图表因缺少列被跳过:\n"
            for chart_name, missing_cols in missing_charts:
                warning_msg += f"- **{chart_name}**: 缺少列 {', '.join(missing_cols)}\n"
            st.warning(warning_msg)
        
       # 3. 动态创建有效图表的布局
        valid_keys = list(valid_charts.keys())
        num_valid = len(valid_keys)
        
        if num_valid == 0:
            st.info("没有有效的图表可以显示")
            return
        
       # 计算需要多少行（每行最多2个图表）
        num_rows = (num_valid + 1) // 2
        for row in range(num_rows):
            cols = st.columns(2)
            
            for col_idx in range(2):
                chart_idx = row * 2 + col_idx
                if chart_idx < num_valid:
                    chart_name = valid_keys[chart_idx]
                    config = valid_charts[chart_name]
                    
                    with cols[col_idx]:
                        st.markdown(f"### {chart_name}")
#================================ 添加图标类型==================================
                        #折线图
                        if config["type"] == "line":
                            st.line_chart(
                                data=df,
                                x=config["x_axis"],
                                y=config["columns"]
                            )
                        # 柱状图
                        elif config["type"] == "bar":
                            st.bar_chart(
                                data=df,
                                x=config["x_axis"],
                                y=config["columns"]
                            )
                            
                                                  
                        # 散点图
                        elif config["type"] == "scatter":
                            # 把数据重构为长格式
                            fig = px.scatter(
                                data_frame=df,
                                x=config["x_axis"],
                                y=config["columns"],
                                color="variable",  # 依据原始列名进行颜色区分
                                labels={"value": config["columns"][0],"variable": "数值"}  # 自定义标签
                            )
                            st.plotly_chart(fig, use_container_width=True) 
             
                        # # 饼图
                        elif config["type"] == "pie":
                            # 获取总额列名和部分金额列名
                            total_col = config["x_axis"]
                            part_cols = config["columns"]
                            
                            # 检查列是否存在
                            if total_col not in df.columns or not all(col in df.columns for col in part_cols):
                                st.warning(f"缺少必要的列: {total_col} 或 {', '.join(part_cols)}")
                                continue
                            
                            # 让用户选择行（默认为第二行）
                            row_options = list(range(len(df)))
                            selected_row = st.selectbox(
                                f"选择数据行 ({chart_name})",
                                options=row_options,
                                index=1 if len(row_options) > 1 else 0,
                                key=f"row_select_{chart_name}"
                            )
                            
                            # 获取选中的行数据
                            row_data = df.iloc[selected_row]
                            
                            # 获取总额值
                            total_value = row_data[total_col]
                            
                            # 计算各部分金额
                            part_values = []
                            part_labels = []
                            for col in part_cols:
                                value = row_data[col]
                                part_values.append(value)
                                part_labels.append(f"{col} ({value:.2f})")
                            
                            # 计算"其他"部分
                            parts_sum = sum(part_values)
                            other_value = total_value - parts_sum
                            if other_value > 0:
                                part_values.append(other_value)
                                part_labels.append(f"其他 ({other_value:.2f})")
                            
                            # 创建饼图
                            fig = px.pie(
                                values=part_values,
                                names=part_labels,
                                title=f"{chart_name} (第{selected_row+1}行)",
                                hover_data=[part_values],
                                hole=0.3  # 中间留空，形成环形图
                            )
                            
                            # 添加总额注释
                            fig.update_layout(
                                annotations=[
                                    dict(
                                        text=f'总额: {total_value:.2f}',
                                        showarrow=False,
                                        x=0.5, y=0.5,
                                        font_size=14
                                    )
                                ]
                            )
                            
                            # 显示图表
                            st.plotly_chart(fig, use_container_width=True)
                        # elif config["type"] == "pie":
                        #     # 获取总额列名和部分金额列名
                        #     total_col = config["x_axis"]
                        #     part_cols = config["columns"]
                            
                        #     # 检查列是否存在
                        #     if total_col not in df.columns or not all(col in df.columns for col in part_cols):
                        #         st.warning(f"缺少必要的列: {total_col} 或 {', '.join(part_cols)}")
                        #         continue
                            
                        #     # 创建行标签 - 使用索引或第一列的值
                        #     row_labels = []
                        #     for idx, row in df.iterrows():
                        #         # 尝试使用索引作为标签（如果索引有意义）
                        #         if isinstance(df.index, pd.RangeIndex):
                        #             label = f"行 {idx+1}"
                        #         else:
                        #             label = str(idx)
                                
                        #         # 添加首列值（如果存在）使标签更丰富
                        #         if len(df.columns) > 0:
                        #             first_col = df.columns[0]
                        #             label += f": {row[first_col]}"
                                
                        #         row_labels.append(label)
                            
                        #     # 让用户选择行（默认第一行）
                        #     selected_label = st.selectbox(
                        #         f"选择数据行 ({chart_name})",
                        #         options=row_labels,
                        #         index=0,  # 默认选择第一行
                        #         key=f"row_select_{chart_name}"
                        #     )
                            
                        #     # 获取选中的行索引
                        #     selected_row = row_labels.index(selected_label)
                            
                        #     # 获取选中的行数据
                        #     row_data = df.iloc[selected_row]
                            
                        #     # 获取总额值
                        #     total_value = row_data[total_col]
                            
                        #     # 计算各部分金额
                        #     part_values = []
                        #     part_labels = []
                        #     for col in part_cols:
                        #         value = row_data[col]
                        #         part_values.append(value)
                        #         part_labels.append(f"{col} ({value:.2f})")
                            
                        #     # 计算"其他"部分
                        #     parts_sum = sum(part_values)
                        #     other_value = total_value - parts_sum
                        #     if other_value > 0:
                        #         part_values.append(other_value)
                        #         part_labels.append(f"其他 ({other_value:.2f})")
                            
                        #     # 创建饼图
                        #     fig = px.pie(
                        #         values=part_values,
                        #         names=part_labels,
                        #         hover_data=[part_values],
                        #         hole=0.3  # 中间留空，形成环形图
                        #     )
                            
                        #     # 添加总额注释
                        #     fig.update_layout(
                        #         annotations=[
                        #             dict(
                        #                 text=f'总额: {total_value:.2f}',
                        #                 showarrow=False,
                        #                 x=0.5, y=0.5,
                        #                 font_size=14
                        #             )
                        #         ]
                        #     )
                            
                        #     # 显示图表
                        #     st.plotly_chart(fig, use_container_width=True)
                            
                        #面积图
                        elif config["type"] == "area":
                            st.area_chart(
                                data=df,
                                x=config["x_axis"],
                                y=config["columns"]
                            )
                        
                        # #直方图
                        # elif config["type"] == "hist":
                        #     fig = px.histogram(
                        #         df,
                        #         x=config["x_axis"],
                        #         nbins=config.get("bins", 20),
                        #         color=config.get("color_column", None),
                        #         title=chart_name
                        #     )
                        #     st.plotly_chart(fig, use_container_width=True)
                        
                        # 热力图
                        elif config["type"] == "correlation_heatmap":
                            # 检查所需列是否存在
                            available_cols = [col for col in config["columns"] 
                                            if col in df.columns]
                            missing_cols = [col for col in config["columns"] 
                                          if col not in df.columns]
                            
                            if not available_cols:
                                st.warning(f"所有指定列都不存在: {', '.join(config['columns'])}")
                                continue
                            
                            if missing_cols:
                                st.warning(f"以下列不存在，已跳过: {', '.join(missing_cols)}")
                            
                            # 计算相关性矩阵
                            correlation_df = df[available_cols].corr()
                            
                            # 创建热力图
                            fig = px.imshow(
                                correlation_df,
                                text_auto=".2f",  # 在单元格中显示两位小数的数值
                                color_continuous_scale="RdBu_r",  # 红蓝对比色，反转以使正相关为蓝色
                                aspect="auto",  # 自动调整宽高比
                                labels=dict(color="相关系数"),
                                zmin=-1,  # 设置最小值为-1
                                zmax=1    # 设置最大值为1
                            )
                            
                            # 设置布局
                            fig.update_layout(
                                xaxis_title="指标",
                                yaxis_title="指标",
                                height=max(400, 100 * len(available_cols)),  # 根据指标数量调整高度
                                width=max(500, 150 * len(available_cols))    # 根据指标数量调整宽度
                            )
                            
                            # 添加自定义悬停文本
                            fig.update_traces(
                                hovertemplate=(
                                    "指标1: %{y}<br>" +
                                    "指标2: %{x}<br>" +
                                    "相关系数: %{z:.3f}<extra></extra>"
                                )
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        # 箱线图
                        # elif config["type"] == "box":
                        #     fig = px.box(
                        #         df,
                        #         y=config["columns"],
                        #         x=config.get("x_axis", None),
                        #         color=config.get("color_column", None),
                        #         title=chart_name
                        #     )
                        #     st.plotly_chart(fig, use_container_width=True)
                        # 在现有的图表类型判断条件中添加以下代码：
                        elif config["type"] == "grouped_bar":
                            # 准备数据
                            fig = go.Figure()
                            
                            # 颜色设置
                            colors = ['#636EFA', '#EF553B']  # A组和B组颜色
                            
                            # 计算x轴位置
                            x_positions = list(range(len(df[config["x_axis"]].unique())))
                            a_positions = [x - 0.15 for x in x_positions]  # A组向左偏移
                            b_positions = [x + 0.15 for x in x_positions]  # B组向右偏移
                            
                            # 绘制A组柱子
                            fig.add_trace(go.Bar(
                                x=a_positions,
                                y=df[config["columns"][0]],
                                name=config["group_names"][0],
                                marker_color=colors[0],
                                width=0.3,
                                text=df[config["columns"][0]],  # 显示数值标签
                                textposition='outside'
                            ))
                            
                            # 绘制B组柱子
                            fig.add_trace(go.Bar(
                                x=b_positions,
                                y=df[config["columns"][1]],
                                name=config["group_names"][1],
                                marker_color=colors[1],
                                width=0.3,
                                text=df[config["columns"][1]],  # 显示数值标签
                                textposition='outside'
                            ))
                            
                            # 更新布局
                            fig.update_layout(
                                barmode='group',  # 关键设置：分组模式
                                #title=chart_name,
                                xaxis={
                                    'tickvals': x_positions,
                                    'ticktext': df[config["x_axis"]].unique(),
                                    'title': config["x_axis"]
                                },
                                yaxis={'title': '数值'},
                                hovermode='x unified',
                                bargap=0.2,
                                bargroupgap=0.1  # 组内柱子间距
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)

                                                # 双轴折线图
                        elif config["type"] == "dual_axis_line":
                            # 检查所需列是否存在
                            required_cols = [config["x_axis"]] + config["columns"] + config["right_columns"]
                            missing_cols = [col for col in required_cols if col not in df.columns]
                            
                            if missing_cols:
                                st.warning(f"缺少列: {', '.join(missing_cols)}")
                                continue
                            
                            # 创建双轴图表
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            
                            # 添加左侧Y轴数据
                            for col in config["columns"]:
                                fig.add_trace(
                                    go.Scatter(
                                        x=df[config["x_axis"]],
                                        y=df[col],
                                        name=col,
                                        mode='lines+markers',
                                        line=dict(width=2.5)
                                    ),
                                    secondary_y=False
                                )
                            
                            # 添加右侧Y轴数据
                            for col in config["right_columns"]:
                                fig.add_trace(
                                    go.Scatter(
                                        x=df[config["x_axis"]],
                                        y=df[col],
                                        name=col,
                                        mode='lines+markers',
                                        line=dict(width=2.5, dash='dash')
                                    ),
                                    secondary_y=True
                                )
                            
                            # 设置布局
                            fig.update_layout(
                                title=chart_name,
                                xaxis_title=config["x_axis"],
                                legend_title="指标",
                                hovermode="x unified",
                                height=400
                            )
                            
                            # 设置Y轴标题
                            fig.update_yaxes(
                                title_text=config.get("left_title", "左侧指标"),
                                secondary_y=False
                            )
                            fig.update_yaxes(
                                title_text=config.get("right_title", "右侧指标"),
                                secondary_y=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)

#=========================================================================
# 侧边栏导航
def render_sidebar(state):
    with st.sidebar:
        st.title("📊 数据分析平台")

        st.divider()
        
        # 页面导航
        st.subheader("功能模块")
        page_options = {
            "数据导入": "📥",
            "数据清洗": "🧹",
            "数据看板": "📊"
        }
        
        for page, icon in page_options.items():
            if st.button(f"{icon} {page}", use_container_width=True, key=f"nav_{page}"):
                state.current_page = page
        
        st.divider()
        
        # 数据状态
        st.subheader("数据状态")
        if state.file_uploaded:
            st.success("数据已加载")
            if state.raw_df is not None:
                st.caption(f"原始数据: {state.raw_df.shape[0]}行 × {state.raw_df.shape[1]}列")
            if state.cleaned_df is not None:
                st.caption(f"清洗后数据: {state.cleaned_df.shape[0]}行 × {state.cleaned_df.shape[1]}列")
        else:
            st.warning("未加载数据")
        
        # 重置按钮
        if st.button("重置所有数据", use_container_width=True, type="secondary"):
            state.reset_data()
            st.rerun()
        
        st.divider()
        st.caption("版本: v1.0.0 | 开发中")

# 主应用
def main():
    # 页面设置
    st.set_page_config(
        page_title="龙数-数据分析平台",
        layout="wide",      #布局模式
        initial_sidebar_state="expanded",
        page_icon="🐲"
    )
    
    # 初始化全局状态
    state = init_global_state()
    
    # 渲染侧边栏
    render_sidebar(state)
    
    # 渲染当前页面
    if state.current_page == "数据导入":
        DataImportModule(state).render()
    elif state.current_page == "数据清洗":
        DataCleaningModule(state).render()
    elif state.current_page == "数据看板":
        DashboardModule(state).render()

if __name__ == "__main__":
    main()