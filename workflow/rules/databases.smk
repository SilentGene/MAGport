# Database verification
def check_db_path(db_path, db_name):
    """Check if database path is configured and exists"""
    db_path = Path(db_path)
    env_var = f"{db_name.upper()}_DB_PATH"
    
    if not db_path or str(db_path) == "":
        raise ValueError(
            f"{db_name} database path is not configured. "
            f"Please either:\n"
            f"1. Set {env_var} environment variable, or\n"
            f"2. Configure {db_name.lower()}_db_dir in config.yaml, or\n"
            f"3. Run 'magport download --{db_name.lower()}-path /path/to/download/location' to download it"
        )
    
    if not db_path.exists():
        raise ValueError(
            f"{db_name} database not found at {db_path}. "
            f"Please either:\n"
            f"1. Create the directory and provide the database, or\n"
            f"2. Run 'magport download --{db_name.lower()}-path /path/to/download/location' to download it"
        )

def verify_all_databases():
    """Verify all required databases before workflow starts"""
    # 获取全局变量
    global MODULES, USE_CHECKM
    global GTDBTK_DB, CHECKM2_DB, CHECKM1_DB, GUNC_DB, NCBI16S_DIR
    
    try:
        # 检查哪些模块被启用
        enabled_modules = set(MODULES)
        
        # 根据启用的模块验证相应的数据库
        if "gtdb" in enabled_modules:
            check_db_path(GTDBTK_DB, "GTDBTK")
        
        if "quality" in enabled_modules:
            if USE_CHECKM == "checkm2":
                check_db_path(CHECKM2_DB, "CHECKM2")
            else:
                check_db_path(CHECKM1_DB, "CHECKM1")
        
        if "gunc" in enabled_modules:
            check_db_path(GUNC_DB, "GUNC")
        
        if "rrna16S" in enabled_modules:
            check_db_path(NCBI16S_DIR, "NCBI16S")
    except NameError as e:
        print(f"[MAGport] Warning: Could not verify databases - {e}")
        print("[MAGport] This is normal if you're just viewing the DAG or doing a dry run.")


