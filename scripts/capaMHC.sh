# 输入参数定义
sample=$1
mutation_type=$2
hlaI=$3
outdir=$4
MS_filter_file=$5

# 获取脚本所在目录的路径
script_dir=$(dirname "$0")

# 转换为绝对路径
script_dir_abs=$(cd "$script_dir" && pwd)

# 获取脚本所在目录的上级目录
parent_dir=$(dirname "$script_dir_abs")

data_dir="$parent_dir/data"
echo data_dir: ${data_dir}
scripts_dir="$parent_dir/scripts"
echo scripts_dirs: ${scripts_dirs}
awk -F '\t' '$4!="Sq"   {print$4}' ${data_dir}/upload/${MS_filter_file}  > ${data_dir}/temp/${sample}.${mutation_type}.MAPS-1.fasta
sort  ${data_dir}/temp/${sample}.${mutation_type}.MAPS-1.fasta |uniq  > ${data_dir}/temp/${sample}.${mutation_type}.MAPS-2.fasta
awk -v x=7 '{if(length($1)>x){print $0}}' ${data_dir}/temp/${sample}.${mutation_type}.MAPS-2.fasta > ${data_dir}/temp/${sample}.${mutation_type}.MAPS.fasta
rm ${data_dir}/temp/${sample}.${mutation_type}.MAPS-1.fasta ${data_dir}/temp/${sample}.${mutation_type}.MAPS-2.fasta

echo "${scripts_dir}/length.py"
python ${scripts_dir}/length.py ${data_dir}/upload/${MS_filter_file}  ${data_dir}/temp/${sample}.${mutation_type}-1.csv
cat   ${data_dir}/temp/${sample}.${mutation_type}-1.csv |awk '!a[$4]++{print}'> ${data_dir}/temp/${sample}.${mutation_type}.csv
#rm ${data_dir}/temp/${sample}.${mutation_type}-1.csv
echo $(date) ${sample}.${mutation_type}.csv finished ...

## 切换到输出目录
#cd $outdir
#
# HLA 预测处理
#for hla in `cat $hlaI`
#do
#    netMHCpan-4.0/netMHCpan -a $hla -p -inptype 1 -l 8,9,10,11 -s -f $data_dir/upload/${sample}-${mutation_type}.MAPS.fasta  -BA > $data_dir/temp/${sample}.$hla.binding.xls
#done
#echo $(date) ${sample}.MHCI.$hla.binding.xls  finished ...
#
## 生成 HLA 绑定文件的列表
ls $data_dir/temp/${sample}.*.binding.xls > $data_dir/temp/${sample}.MHCI.binding.list

# 合并所有 HLA 绑定数据
perl ${scripts_dir}/combine.MHC.binding.pl $data_dir/temp/${sample}.MHCI.binding.list $data_dir/temp/${sample}.MHCI.binding.merge.txt
echo $(date) ${sample}.MHCI.binding.merge.txt  finished ...

# 结合突变数据和 HLA 绑定数据
perl ${scripts_dir}/combineMS.MHC.pl $data_dir/temp/${sample}.${mutation_type}.csv $data_dir/temp/${sample}.MHCI.binding.merge.txt $data_dir/temp/${sample}.capaMHC.MHCbinding.csv
echo $(date) ${sample}.capaMHC.MHCbinding.csv finished ...

## 过滤出最终的 MHC 绑定数据
awk -F '\t' '{if( $(NF-1) == "Min_rank" || $(NF-1) < 2) {print}}' $data_dir/temp/${sample}.capaMHC.MHCbinding.csv > $data_dir/temp/${sample}.capaMHC.MHCbinding.final.csv
sed -i '' 's/\r//g' $data_dir/temp/${sample}.capaMHC.MHCbinding.final.csv
echo $(date) ${sample}.capaMHC.MHCbinding.final.csv finished ...