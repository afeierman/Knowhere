def Read_csv(user, file_with_path):
    import pandas as pd
    import numpy as np
    df = pd.read_csv(file_with_path,error_bad_lines=False,index_col=0,skiprows=0)
    df.index = df.index.to_datetime()
    columns = list(df.columns)
    df.rename(columns={columns[0]: "sensor", columns[1]: "data_name", columns[2]:"data_display", columns[3]:"data_raw"}, inplace=True)
    df['_user_id'] = user
    return(df)
    
def Clean_iPhone_Data(df):
    import numpy as np
    import pandas as pd
    df = df.applymap(lambda x: str.strip(x))
    df = df.applymap(lambda x: pd.to_numeric(x, errors='ignore'))
    df = df[(df.data_name != 'Enabled')]
    df = df[(df.data_name != 'Authorisation Status')]
    df = df[(df.data_name != 'Floor')]
    return(df)


