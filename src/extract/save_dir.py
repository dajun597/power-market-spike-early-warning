from pathlib import Path

def saved_data_dir(name,file,output_dir):
    output_dir = Path(output_dir)
    if output_dir.exists():
        file_path=output_dir.joinpath(name)
        file.to_csv(file_path,index=False)
        print(f'{name} saved to {file_path.resolve()}')
    else:
        print(f'{output_dir} does not exist')



