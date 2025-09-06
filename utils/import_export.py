import pandas as pd
import os
from datetime import datetime
from models.asset import Asset
from database import Database

class ImportExport:
    @staticmethod
    def export_assets(file_path, filters=None):
        """导出资产数据到Excel文件"""
        try:
            # 获取所有资产
            assets = Asset.get_all_assets(filters)
            
            # 准备导出数据
            data = []
            for asset in assets:
                # 资产基础信息
                asset_info = {
                    "资产编号": asset[1],
                    "设备名称": asset[2],
                    "数量": asset[3],
                    "类目": asset[4],
                    "品牌规格": asset[5],
                    "入库时间": asset[6],
                    "设备位置": asset[8],
                    "维修状态": asset[10],
                    "备注": asset[9]
                }
                
                # 获取使用人信息
                db = Database()
                users = db.fetchall(
                    "SELECT user_name, start_date, end_date FROM asset_users WHERE asset_id = ?",
                    (asset[0],)
                )
                
                # 添加使用人信息
                for i, user in enumerate(users, 1):
                    asset_info[f"使用人{i}"] = user[0]
                    asset_info[f"使用开始时间{i}"] = user[1]
                    asset_info[f"使用结束时间{i}"] = user[2] if user[2] else ""
                
                # 获取维修记录
                repairs = db.fetchall(
                    """SELECT repair_date, fault_cause, repair_result 
                       FROM repair_records WHERE asset_id = ?""",
                    (asset[0],)
                )
                
                # 添加维修记录
                for i, repair in enumerate(repairs, 1):
                    asset_info[f"维修时间{i}"] = repair[0]
                    asset_info[f"故障原因{i}"] = repair[1]
                    asset_info[f"维修结果{i}"] = repair[2]
                
                data.append(asset_info)
            
            # 创建DataFrame并导出到Excel
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            return True, "导出成功"
        except Exception as e:
            return False, f"导出失败: {str(e)}"
    
    @staticmethod
    def import_assets(file_path, user_id):
        """从Excel文件导入资产数据"""
        try:
            if not os.path.exists(file_path):
                return False, "文件不存在"
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 检查必要的列是否存在
            required_columns = ["资产编号", "设备名称", "类目"]
            for col in required_columns:
                if col not in df.columns:
                    return False, f"缺少必要的列: {col}"
            
            success_count = 0
            error_count = 0
            errors = []
            
            # 遍历每一行数据
            for index, row in df.iterrows():
                try:
                    # 创建资产对象
                    asset = Asset(str(row["资产编号"]))
                    
                    # 如果资产已存在，则跳过或更新
                    if asset.id:
                        error_count += 1
                        errors.append(f"行 {index+1}: 资产编号 {row['资产编号']} 已存在")
                        continue
                    
                    # 设置资产属性
                    asset.name = str(row["设备名称"]) if pd.notna(row["设备名称"]) else ""
                    asset.category = str(row["类目"]) if pd.notna(row["类目"]) else ""
                    asset.quantity = int(row["数量"]) if pd.notna(row["数量"]) else 1
                    asset.brand_spec = str(row["品牌规格"]) if pd.notna(row["品牌规格"]) else ""
                    asset.purchase_date = str(row["入库时间"]) if pd.notna(row["入库时间"]) else None
                    asset.location = str(row["设备位置"]) if pd.notna(row["设备位置"]) else ""
                    asset.notes = str(row["备注"]) if pd.notna(row["备注"]) else ""
                    
                    # 保存资产
                    success, msg = asset.save(user_id)
                    if success:
                        success_count += 1
                        
                        # 处理使用人信息
                        i = 1
                        while f"使用人{i}" in df.columns and pd.notna(row[f"使用人{i}"]):
                            user_name = str(row[f"使用人{i}"])
                            start_date = str(row[f"使用开始时间{i}"]) if pd.notna(row[f"使用开始时间{i}"]) else str(datetime.now().date())
                            end_date = str(row[f"使用结束时间{i}"]) if pd.notna(row[f"使用结束时间{i}"]) else None
                            
                            asset.add_user(user_name, start_date, end_date)
                            i += 1
                        
                        # 处理维修记录
                        i = 1
                        while f"维修时间{i}" in df.columns and pd.notna(row[f"维修时间{i}"]):
                            repair_date = str(row[f"维修时间{i}"])
                            fault_cause = str(row[f"故障原因{i}"]) if pd.notna(row[f"故障原因{i}"]) else ""
                            repair_result = str(row[f"维修结果{i}"]) if pd.notna(row[f"维修结果{i}"]) else ""
                            
                            asset.add_repair_record(repair_date, fault_cause, repair_result, user_id)
                            i += 1
                    else:
                        error_count += 1
                        errors.append(f"行 {index+1}: {msg}")
                except Exception as e:
                    error_count += 1
                    errors.append(f"行 {index+1}: 处理错误 - {str(e)}")
            
            return True, f"导入完成。成功: {success_count}, 失败: {error_count}。\n" + "\n".join(errors[:10])
        except Exception as e:
            return False, f"导入失败: {str(e)}"
