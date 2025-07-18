import pandas as pd
import os

"""
2. 筛选前几位客户明细
"""
PARAM_PROMPTS = {
    'input_pathA': '请输入原始表格路径：',
    'input_pathB': '请输入筛选条件表格路径：',
    'output_dir': "请输入输出文件夹的绝对路径：",
    'date_prefix': '请输入输出文件的日期前缀：',
    'row_ranges': '请输入行索引范围（可以输入多个范围，用逗号分隔；例如：0-5,10-15）：',
    'extra_conditions': "请输入额外的固定值筛选条件（按列设置，可以输入多个条件）：\n例如：列名=工单小类,值=签收延误,派送延误\n请输入条件（格式：列名=值1,值2,...）："
}

def parse_row_ranges(row_ranges_str, data_length):
    """
    解析行索引范围字符串为具体的行索引列表
    """
    row_indices = []
    try:
        ranges = row_ranges_str.split(',')
        for r in ranges:
            r = r.strip()
            if '-' in r:
                start, end = r.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if start < 0 or end >= data_length or start > end:
                    print(f"无效的行索引范围：{r}，跳过此范围。")
                    continue
                row_indices.extend(range(start, end+1))
            else:
                index = int(r.strip())
                if index < 0 or index >= data_length:
                    print(f"无效的行索引：{r}，跳过此索引。")
                    continue
                row_indices.append(index)
    except Exception as e:
        raise ValueError(f"行索引范围格式不正确：{str(e)}")
    
    return list(set(row_indices))  # 去重并返回

def main(input_pathA=None, input_pathB=None, output_dir=None, date_prefix=None, row_ranges=None, extra_conditions=None):
    try:
        # 去除路径中的引号
        input_pathA = input_pathA.strip('"') if input_pathA else None
        input_pathB = input_pathB.strip('"') if input_pathB else None
        output_dir = output_dir.strip('"') if output_dir else None
        
        # 检查所有必需参数是否已提供
        if not all([input_pathA, input_pathB, output_dir, date_prefix, row_ranges]):
            missing_params = []
            if not input_pathA: missing_params.append('input_pathA')
            if not input_pathB: missing_params.append('input_pathB')
            if not output_dir: missing_params.append('output_dir')
            if not date_prefix: missing_params.append('date_prefix')
            if not row_ranges: missing_params.append('row_ranges')
            
            raise ValueError(f"缺少必要的参数：{', '.join(missing_params)}")
        
        # 检查文件路径是否存在
        if not os.path.exists(input_pathA):
            raise ValueError(f"原始表格路径不存在: {input_pathA}")
        
        if not os.path.exists(input_pathB):
            raise ValueError(f"筛选条件表格路径不存在: {input_pathB}")
        
        # 检查文件格式
        if not input_pathA.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise ValueError("原始表格格式不支持，请使用Excel或CSV文件")
        
        if not input_pathB.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise ValueError("筛选条件表格格式不支持，请使用Excel或CSV文件")
        
        # 读取表格A
        if input_pathA.lower().endswith(('.xlsx', '.xls')):
            df_a = pd.read_excel(input_pathA)
        elif input_pathA.lower().endswith('.csv'):
            df_a = pd.read_csv(input_pathA)
        else:
            raise ValueError("原始表格格式不支持，请使用Excel或CSV文件")
        
        print(f"原始表格A共有 {len(df_a)} 行数据。")
        print("原始表格A的列名：", df_a.columns)
        print("原始表格A的前10行数据：")
        print(df_a.head(10))
        
        # 读取表格B
        if input_pathB.lower().endswith(('.xlsx', '.xls')):
            df_b = pd.read_excel(input_pathB)
        elif input_pathB.lower().endswith('.csv'):
            df_b = pd.read_csv(input_pathB)
        else:
            raise ValueError("筛选条件表格格式不支持，请使用Excel或CSV文件")
        
        print("筛选条件表格B的列名：", df_b.columns)
        print('筛选表格的前10行数据为：')
        print(df_b.head(10))
        
        # 提取表格B中作为筛选条件的列
        required_columns = ['揽收网点名称', 'K码', '客户名称']
        if not all(col in df_b.columns for col in required_columns):
            print(f"筛选条件表格中缺少必要的列：{', '.join(required_columns)}")
            return
        
        # 解析行索引范围
        try:
            row_indices = parse_row_ranges(row_ranges, len(df_b))
            conditions_b = df_b[required_columns].iloc[row_indices]
        except ValueError as e:
            raise ValueError(f"行索引范围解析错误：{str(e)}")
        
        # 打印条件数据，供用户检查
        print("用于筛选的条件数据：")
        print(conditions_b)
        
        # 应用额外的固定值筛选条件
        if extra_conditions:
            conditions = extra_conditions.split(';')
            for condition in conditions:
                if '=' in condition:
                    parts = condition.split('=', 1)
                    if len(parts) != 2:
                        print(f"条件格式无效：{condition}，跳过此条件。")
                        continue
                    
                    col, values = parts
                    col = col.strip()
                    values = [value.strip() for value in values.split(',')]
                    
                    # 验证列名是否有效
                    if col not in df_a.columns:
                        print(f"列名 '{col}' 不存在于表格A中，跳过此条件。")
                        continue
                    
                    # 检查列的数据类型，并转换输入值
                    if pd.api.types.is_numeric_dtype(df_a[col]):
                        try:
                            values = [float(value) if '.' in value else int(value) for value in values]
                        except ValueError:
                            print(f"输入的值 {values} 无法转换为数字，跳过此条件。")
                            continue
                    elif pd.api.types.is_datetime64_dtype(df_a[col]):
                        try:
                            values = [pd.to_datetime(value) for value in values]
                        except ValueError:
                            print(f"输入的值 {values} 无法转换为日期时间，跳过此条件。")
                            continue
                    
                    # 应用固定值筛选条件
                    mask = df_a[col].isin(values)
                    df_a = df_a[mask]
                    print(f"应用条件 '{col} in {values}' 后的表格A数据行数：", len(df_a))
                else:
                    print(f"条件格式无效：{condition}，跳过此条件。")
        
        # 检查应用条件后表格A是否有数据
        if len(df_a) == 0:
            raise ValueError("应用条件后，表格A没有剩余数据。")
        
        # 合并表格A和表格B
        filtered_df = pd.merge(df_a, conditions_b, on=required_columns, how='inner')
        print("合并后的数据框行数：", len(filtered_df))
        
        if len(filtered_df) == 0:
            raise ValueError("合并后没有数据满足条件，请检查筛选条件是否正确。")
        
        # 保存筛选结果
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        file_name = f"{date_prefix}-前几位客户明细.xlsx"
        file_path = os.path.join(output_dir, file_name)
        filtered_df.to_excel(file_path, index=False)
        
        print(f"筛选完成！结果已保存到 {file_path}")
        print(f"原始表格A有 {len(df_a)} 行，筛选后得到 {len(filtered_df)} 行。")
        
        # 保存单号列到新的Excel文件
        if '单号' in filtered_df.columns:
            file_name = f"{date_prefix}-筛选后客户运单号列表.xlsx"
            file_path = os.path.join(output_dir, file_name)
            filtered_df[['单号']].to_excel(file_path, index=False)
            print(f"单号列表已保存到 {file_path}")
        else:
            print("合并后的数据表中没有找到“单号”列，无法保存单号列表。")
        
        return {'success': True, 'message': "操作成功完成！" }
    
    except Exception as e:
        return {'success': False, 'message': str(e) }

# 如果直接运行此脚本（而非被导入），则可以从命令行获取参数并调用 filter_data_by_conditions 函数
if __name__ == "__main__":
    input_pathA = input('请输入原始表格路径：').strip('"')
    input_pathB = input('请输入筛选条件表格路径：').strip('"')
    output_dir = input("请输入输出文件夹的绝对路径：").strip('"')
    date_prefix = input('请输入输出文件的日期前缀：').strip('"')
    row_ranges = input('请输入行索引范围（例如：0-5,10-15）：').strip('"')
    result = main(input_pathA, input_pathB, output_dir, date_prefix, row_ranges)
    print(result['message'])