# Create your views here.
import os
import re
import subprocess
import pandas as pd

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import FileUploadForm

trim_24_jf_path = '/data3/huomiaozhe/tsa_data/trim.24.jf-input'
spe_assembly_fasta_path = '/data3/huomiaozhe/tsa_data/spe-assembly.fasta-input'

@csrf_exempt
@require_http_methods(["POST"])
def test(request):
    return JsonResponse({'status': 'success', 'result': 'hello, world'})


@csrf_exempt
@require_http_methods(["POST"])
def get_result(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_file = request.FILES['file']
        pattern = re.compile(r'^(.+?)-(.+)\.txt$')
        match = pattern.match(uploaded_file.name)
        if not match:
            return HttpResponse("File name format invalid", status=400)

        sample = match.group(1)
        mutation_type = match.group(2)

        current_path = os.getcwd()
        data_path = os.path.join(current_path, 'data')

        output_file = os.path.join(data_path, 'output', mutation_type, f'{sample}.control.jf.csv')
        df = pd.read_csv(output_file, delimiter='\t')
        json_data = df.to_json(orient='records')
        return JsonResponse({'status': 'success', 'result': json_data})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors})




@csrf_exempt
@require_http_methods(["POST"])
def process_file(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        print('form.is_valid')
        # 处理文件
        uploaded_file = request.FILES['file']

        result = handle_uploaded_file(uploaded_file)

        return JsonResponse({'status': 'success', 'result': result})
    else:
        print('form.is_not_valid')
        return JsonResponse({'status': 'error', 'errors': form.errors})


def handle_uploaded_file(f):
    # 保存文件到临时位置或者直接处理
    with open('./data/upload/' + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    # 假设有一个外部脚本可以处理这个文件
    result = run_script(f.name)
    return result


def run_script(file_name):
    pattern = re.compile(r'^(.+?)-(.+)\.txt$')
    match = pattern.match(file_name)
    if not match:
        return HttpResponse("File name format invalid", status=400)

    sample = match.group(1)
    mutation_type = match.group(2)

    print("sample", sample)
    print("mutation_type", mutation_type)

    # 这里调用外部脚本处理文件
    # 设置脚本参数
    # sample = "sample_identifier"  # 示例，你可能需要根据实际情况修改
    # mutation_type = "type1"  # 示例，你可能需要根据实际情况修改
    outdir = './data'  # 输出目录设为文件保存目录
    hlaI = outdir + '/resources/HLA/' + sample + '.hlaI.txt'  # 假设上传的文件就是需要的 HLA 文件

    # 构建脚本路径
    script_path1 = './scripts/capaMHC.sh'
    #
    # 调用 Bash 脚本
    try:
        result = subprocess.run(
            ['bash', script_path1, sample, mutation_type, hlaI, outdir, file_name],
            check=True,  # 检查过程中的错误
            text=True,  # 处理文本输出
            capture_output=True  # 捕获输出
        )
    except subprocess.SubprocessError as e:
        print(e)


    # 获取当前路径 djangoProject
    current_path = os.getcwd()

    script_path = os.path.join(current_path, 'scripts')
    data_path = os.path.join(current_path, 'data')

    run_control_fasta(sample, script_path, data_path)

    if mutation_type == 'spe':
        print('run_control_jf_spe')
        run_control_jf_spe(sample, script_path, data_path)
    elif mutation_type == 'E':
        print('run_control_jf_edit')
        run_control_jf_edit(sample, script_path, data_path)
    elif mutation_type == 'SNP':
        print('run_control_jf_snp')
        run_control_jf_snp(sample, script_path, data_path)
    elif mutation_type == 'INDEL':
        print('run_control_jf_indel')
        run_control_jf_indel(sample, script_path, data_path)
    elif mutation_type == 'FUSION':
        print('run_control_jf_fusion')
        run_control_jf_fusion(sample, script_path, data_path)
    elif mutation_type == 'A3S' or mutation_type == 'A5S' or mutation_type == 'MXE' or mutation_type == 'RI' or mutation_type == 'SE':
        print('run_control_jf_AS')
        run_control_jf_AS(sample, script_path, data_path)

    output_file = os.path.join(data_path, 'output', f'{sample}.control.jf.csv')
    df = pd.read_csv(output_file, delimiter='\t')
    # 将 DataFrame 转换为 JSON 字符串
    json_data = df.to_json(orient='records')
    delete_file(os.path.join('./data/upload/', file_name))
    return json_data


def run_control_fasta(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.fasta.py',
        f'{data_path}/temp/{sample}.capaMHC.MHCbinding.final.csv',
        f'{data_path}/resources/control_control_reformat_70char.fasta',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv'
    ]
    subprocess.run(cmd)


def run_control_jf_spe(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.jf.spe.py',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv',
        f'{trim_24_jf_path}/control.trim.24.jf',
        f'{trim_24_jf_path}/{sample}.trim.24.jf',
        f'{data_path}/output/spe/{sample}.control.jf.csv',
        f'{spe_assembly_fasta_path}/{sample}.assembly.fasta'
    ]
    subprocess.run(cmd)


def run_control_jf_edit(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.jf.edit-snp-indel.py',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv',
        f'{trim_24_jf_path}/control.trim.24.jf',
        f'{trim_24_jf_path}/{sample}.trim.24.jf',
        f'{data_path}/output/{sample}.control.jf.csv',
        f'{data_path}/resources/assembly-fasta/{sample}.candidate.contig.fasta'
    ]
    subprocess.run(cmd)


def run_control_jf_snp(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.jf.edit-snp-indel.py',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv',
        f'{trim_24_jf_path}/control.trim.24.jf',
        f'{trim_24_jf_path}/{sample}.trim.24.jf',
        f'{data_path}/output/{sample}.control.jf.csv',
        f'{data_path}/resources/assembly-fasta/{sample}.indel.contig.fasta'
    ]
    subprocess.run(cmd)


def run_control_jf_indel(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.jf.edit-snp-indel.py',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv',
        f'{trim_24_jf_path}/control.trim.24.jf',
        f'{trim_24_jf_path}/{sample}.trim.24.jf',
        f'{data_path}/output/{sample}.control.jf.csv',
        f'{data_path}/resources/assembly-fasta/{sample}.snp.contig.fasta'
    ]
    subprocess.run(cmd)


def run_control_jf_fusion(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.jf.fusion.py',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv',
        f'{trim_24_jf_path}/control.trim.24.jf',
        f'{trim_24_jf_path}/{sample}.trim.24.jf',
        f'{data_path}/output/{sample}.control.jf.csv',
        f'{data_path}/resources/assembly-fasta/{sample}.finspector.fa'
    ]
    subprocess.run(cmd)


def run_control_jf_AS(sample, script_path, data_path):
    cmd = [
        'python', f'{script_path}/control.jf.AS.py',
        f'{data_path}/resources/control-fasta-csv/{sample}.control.fasta.csv',
        f'{trim_24_jf_path}/control.trim.24.jf',
        f'{trim_24_jf_path}/{sample}.trim.24.jf',
        f'{data_path}/output/{sample}.control.jf-3.csv',
        f'{data_path}/resources/assembly-fasta/{sample}.bam'
    ]
    subprocess.run(cmd)


def delete_file(file_path):
    """
    删除指定路径的文件。

    参数:
        file_path (str): 要删除的文件的完整路径。

    返回:
        bool: 如果文件成功删除，则返回 True；如果文件不存在或删除失败，则返回 False。
    """
    try:
        os.remove(file_path)
        print(f"文件 {file_path} 已被删除。")
        return True
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return False
    except OSError as e:
        print(f"删除文件时出错：{e}")
        return False
