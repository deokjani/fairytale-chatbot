import subprocess
import tempfile
import os
import csv
from typing import Dict, Optional


def run_l2sca(text: str, l2sca_path: str = "/data/edutem/ELA/ai-book_spielraum/L2SCA-2023-08-15") -> Optional[Dict[str, float]]:
    """L2SCA 실행하고 결과 반환"""
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            input_file = f.name
        
        output_file = input_file + '.csv'
        
        # L2SCA 실행
        original_dir = os.getcwd()
        os.chdir(l2sca_path)
        
        result = subprocess.run(
            f"python analyzeText.py {input_file} {output_file}", 
            shell=True, 
            capture_output=True,
            text=True
        )
        
        os.chdir(original_dir)
        
        if result.returncode != 0:
            return None
        
        # 결과 읽기
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            data = next(reader)
        
        # 숫자 변환
        numeric_result = {}
        for key, value in data.items():
            if key != 'Filename':
                try:
                    numeric_result[key] = float(value)
                except:
                    pass
        
        return numeric_result
        
    except Exception:
        return None
    finally:
        # 임시파일 삭제
        for file in [input_file, output_file]:
            if 'file' in locals() and os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass


def get_l2sca_metrics(text: str) -> str:
    """사용자 입력의 L2SCA 지표를 문자열로 반환"""
    result = run_l2sca(text)
    
    if result:
        # 지표 순서 고정 (가독성 향상)
        ordered_keys = ['W', 'S', 'VP', 'C', 'T', 'DC', 'CT', 'CP', 'CN', 
                       'MLS', 'MLT', 'MLC', 'C/S', 'VP/T', 'C/T', 'DC/C', 
                       'DC/T', 'T/S', 'CT/T', 'CP/T', 'CP/C', 'CN/T', 'CN/C']
        
        metrics = ", ".join([f"{k}: {result[k]:.2f}" if isinstance(result[k], float) 
                           else f"{k}: {result[k]}" 
                           for k in ordered_keys if k in result])
        return f"L2SCA metrics - {metrics}"
    else:
        # L2SCA 실패시 LLM이 직접 판단하도록
        return f"Analyze complexity of: '{text}'"