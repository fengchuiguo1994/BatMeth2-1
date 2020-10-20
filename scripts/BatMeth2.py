#!/usr/bin/env python
import os
import sys, getopt
import shutil 
import time

##alignment
threads = 6
mismatches = 0.05
genome_index = ""
input_prefix = "None"
input_prefix1 = ""
input_prefix2 = ""
pairedend="False"
output_prefix = "None"

## fastp
fastp=""

##calmeth
Qual = 10
redup = 0
region = 1000
sammeth = 0
##calmeth and methyGff
coverage = 5
maxcoverage = 1000
binCover = 3
chromstep = 50000

##methyGff
step = 0.025
distance = 2000
gfffile = "None"
bedfile = "None"
GTF = "False"
##mode
mode = "pipel"

## heatmap
CG = 0.6
CHG = 0.2
CHH = 0.1

##aligner
aligner = "BatMeth2" ## bwa-meth bsmap bismark
genome_others = ""

abspath = ""

def usage():
    print "\nBatMeth2 [mode] [paramaters]"
    print "mode:  build_index, pipel, align, calmeth, annoation, methyPlot, batDMR, visul2sample, mkreport, DMCplot"
    print "\n[build_index]"
    print "    Usage: BatMeth2 build_index genomefile. (wgbs data, must run this step first), or"
    print "    Usage: BatMeth2 build_index rrbs genomefile. (rrbs data), or"

    print "\n[pipel (Contains: align, calmeth, annoation, methyPlot, mkreport)]"
    print "    [fastp location]"
    print "    --fastp=    fastp program location."
    print "    ** If --fastp is not defined, the input file should be clean data."
    print "    [select aligner]"
    print "    --aligner=    BatMeth2(default), bwa-meth(v1), bsmap, bismark2, no (exit out_prefix.sam file, no need align again)"
    print "    [other aligners paramaters]"
    print "    --go=    Name of the genome, contaion index build by aligner. (bwa-meth/bismark2)"
    print "    [main paramaters]"
    print "    -o [outprefix]    Name of output file prefix"
    print "    [alignment paramaters]"
    print "    -i    Name of input file, if paired-end. please use -1, -2"
    print "    -1    Name of input file left end, if single-end. please use -i"
    print "    -2    Name of input file right end"
    print "    -i/-1/-2 can be comma-separated lists (no whitespace), only supported in BatMeth2 aligner."
    print "    -g    Name of the genome mapped against, make sure build index first."
    print "    -n    maximum mismatches allowed due to seq. default 0.05 percentage of the read length. [0-0.3]"
    print "    -p <interger>    Launch <integer> threads"
    print "    [calmeth paramaters]"
    print "    --Qual=      calculate the methratio while read QulityScore >= Q. default:10"
    print "    --redup=     REMOVE_DUP, 0 or 1, default 0"
    print "    --region=    Bins for DMR calculate , default 1000bp ."
    print "    -f           for sam format outfile contain methState. [0 or 1], default: 0 (dont output this file)."
    print "    [calmeth and annoation paramaters]"
    print "    --coverage=    >= <INT> coverage. default:5"
    print "    --binCover=    >= <INT> nCs per region. default:3"
    print "    --chromstep=   Chromsome using an overlapping sliding window of 100000bp at a step of 50000bp. default step: 50000(bp)"
    print "    [annoation paramaters]"
    print "    --gtf=/--gff=/--bed=    Gtf or gff file / bed file"
    print "    --distance=    DNA methylation level distributions in body and <INT>-bp flanking sequences. The distance of upstream and downstream. default:2000"
    print "    --step=    Gene body and their flanking sequences using an overlapping sliding window of 5% of the sequence length at a step of 2.5% of the sequence length. So default step: 0.025 (2.5%)"
    print "    -C         <= <INT> coverage. default:1000"
    print "    [MethyPlot paramaters]"
    print "    --CG       CG ratio for heatmap, [0-1], default 0.6"
    print "    --CHG      CHG ratio for heatmap, [0-1], default 0.2"
    print "    --CHH      CHH ratio for heatmap, [0-1], default 0.1"
    print "    [mkreport paramaters]"
    print "    -o [outprefix]"
    print "    make a html report."

    print "\n[align paramaters:]"
    print "    see the details in 'BatMeth2 align'"
    print "\n[calmeth paramaters:]"
    print "    see the details in 'BatMeth2 calmeth'"
    print "\n[annotion paramaters:]"
    print "    see the details in 'BatMeth2 annoation'"
    print "\n[methyPlot paramaters:]"
    print "    see the details in 'BatMeth2 methyPlot'"
    print "\n[batDMR paramaters:]"
    print "    see the details in 'BatMeth2 batDMR'"
    print "\n[visul2sample paramaters:]"
    print "    see the details in 'BatMeth2 visul2sample'\n"

    print "-h|--help   usage\n"

def runprogram(cmd):
    print cmd
    error = os.system(cmd)
    if error != 0:
        print "program %s error!"%cmd
        sys.exit()

def detect_paramater():
    opts, args = getopt.getopt(sys.argv[2:], "hi:1:2:o:n:g:p:f:C:", ["gtf=", "gff=", "bed=", "coverage=", "binCover=", 
        "chromstep=", "step=", "distance=", "Qual=", "region=", "aligner=", "go=", "redup=", "CG=", "CHG=", "CHH=", "fastp="])
    global pairedend, input_prefix, input_prefix1, input_prefix2, output_prefix, genome_index, threads, mismatches, region, Qual, aligner, genome_others, fastp, trim
    global gfffile, GTF, redup, sammeth, CG, CHG, CHH
    for op, value in opts:
#        print op, value
        if op == "-i":
            input_prefix = value
        if op == "-1":
            input_prefix1 = value
        if op == "-2":
            input_prefix2 = value
            pairedend="True"
        elif op == "-o":
            output_prefix = value
        elif op == "-g":
            genome_index = value
        elif op == "-p":
            threads = value
        elif op == "-n":
            mismatches = value
        elif op == "-f":
            sammeth = value
        elif op == "-C":
            maxcoverage = value
        elif op == "--gtf":
            gfffile = value
            GTF = "True"
        elif op == "--fastp":
            fastp = value
        elif op == "--gff":
            gfffile = value
        elif op == "--bed":
            bedfile = value
        elif op == "--coverage":
            coverage = value
        elif op == "--binCover":
            binCover = value
        elif op == "--chromstep":
            chromstep = value
        elif op == "--step":
            step = value
        elif op == "--distance":
            distance = value
        elif op == "--Qual":
            Qual = value
        elif op == "--CG":
            CG = CG
        elif op == "--CHG":
            CHG = CHG
        elif op == "--CHH":
            CHH = CHH
        elif op == "--region":
            region = value
        elif op == "--redup":
            redup = value
        elif op == "--aligner":
            aligner = value
        elif op == "--go":
            genome_others = value
        elif op == "-h":
            usage()
            sys.exit()

if len(sys.argv) < 2:
    usage()
    sys.exit()
elif sys.argv[1] == "--help" or sys.argv[1] == "-help" or sys.argv[1] == "-h":
    usage()
    sys.exit()

mode = sys.argv[1]
path1 = os.path.dirname(__file__)
abspath = os.path.abspath(path1) + "/"

##mkdir
def mkdir(path):
    # remove header ' '
    path=path.strip()
    # remove "\"
    #path=path.rstrip("/")
    isExists=os.path.exists(path)

    if not isExists:
        os.makedirs(path)  
        print path+' workdir done.'
        return True
    else:
        print path+' is exits.'
        return False

def copydir(olddir, newdir):
    olddir=olddir.strip()
    newdir=newdir.strip()
    isExists=os.path.exists(newdir)
    if not isExists:
        shutil.copytree(oldreportdir,newdir)
        print newdir+' workdir done.'
        return True
    else:
        print newdir+' is exits, delete.'
        shutil.rmtree(newdir)
        #cmd = "rm -rf " + newdir
        #runprogram(cmd)
        shutil.copytree(oldreportdir,newdir)
        print newdir+' workdir done.'
        return True

def printStatus():
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Genome: ", genome_index
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Annotation: gtf: ", gfffile, "bed: ", bedfile
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Input file: ", input_prefix, " ", input_prefix1, " ", input_prefix2
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Outfile prefix: ", output_prefix

if mode == "align" and aligner == "BatMeth2":
    if len(sys.argv) < 4:
        cmd = abspath + "batmeth2-align"
        runprogram(cmd)
        sys.exit()

if mode == "pipel" or mode == "align" or mode == "mkreport":
    detect_paramater()

if mode == "pipel" and genome_index == "" and genome_others != "":
    cmd = abspath + "preGenome " + genome_others
    runprogram(cmd)
    genome_index = genome_others

if(sys.argv[1] == "pipel"):
	printStatus()

oldreportdir = abspath + "/../BatMeth2-Report"
workdir = os.getcwd()
mkpath= workdir + "/batmeth2_report_" + output_prefix

def printparamter1():
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Process Paramater file."
    ###paramater file
    #mkdir(mkpath)
    fparamater = mkpath + "/images/Paramater.txt"
    Fparamater = open(fparamater, "w")

    alignmode = "Single-end"
    infiles = input_prefix
    if pairedend == "True":
        alignmode = "Paired-end"
        infiles = input_prefix1 + " || " + input_prefix2
    Sparamater = "Program\tBatMeth2.v1\nWorkdir\t" + workdir + "\nAligner\tBatMeth2-align\nGenome\t" + genome_index + "\nAnnotation\t" + gfffile + "/" + bedfile + "\nOutput-prefix\t"+ output_prefix + "\nInput\t"+ infiles +  "\nAlignment-Mode\t" + alignmode
    Fparamater.write(Sparamater)
    Fparamater.close()

def printparamter2():
    ##paramater2
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Process Pramater file2."
    fparamater2 = mkpath + "/images/Paramater2.txt"
    Fparamater2 = open(fparamater2, "w")
    Sparamater2 = "Paramater\tValue\nThreads\t" + str(threads) + "\nCalmeth\tparamaters\n" + "Quality_Score\t" + str(Qual) + "\nredup\t" + str(redup) +"\n" + "meth region length\t" + str(region) + "\nPrint methstate samfile\t" + str(sammeth) +  "\ncalmeth and methyGff\tparamaters\n" +  "Coverage\t" + str(coverage) + "\nmaxCoverage\t" + str(maxcoverage) + "\nbinCoverage\t" + str(binCover) + "\nchromStep\t" + str(chromstep) + "\nmethyGff\tParamaters\n" + "Gene bins step\t" + str(step) + "\nDistance of upstream and downstream\t"+ str(distance)

    Fparamater2.write(Sparamater2)
    Fparamater2.close()

##for i in range(1, len(sys.argv)):
##  print sys.argv[i]

def calmeth(genome_index, mismatches, inputf, output_prefix, threads):
    if genome_index == "":
        print "Please use -g pramater to defined the genome index location."
        sys.exit()
    if inputf == "None":
        print "Must have input sam file (-i paramater)."
        sys.exit()
    rd = " "
    if redup == "1":
        rd = " -r"
    sammethfile = " "
    if sammeth == "1":
        sammethfile =  " -f " + output_prefix + ".md.sam"
    
    cmd = abspath + "calmeth" + " -g " + genome_index + " -n " + str(mismatches) + " -b " + inputf + " -m " + output_prefix  + rd + sammethfile
    if chromstep != 50000:
        cmd = cmd + " -s " + chromstep
    elif coverage != 5:
        cmd = cmd + " -c " + coverage
    elif binCover != 3:
        cmd = cmd + " -nC " + binCover
    elif Qual != 10:
        cmd = cmd + " -Q " + Qual
    elif region != 1000:
        cmd = cmd + " -R " + region
    runprogram(cmd)
    return

def build_index(para):
    if len(sys.argv) < 2:
        print "Must have genome file."
        sys.exit()
    cmd = abspath + "build_all " + para ##sys.argv[2]
    runprogram(cmd)

def alignmentSingle():
    if aligner == "no":
        return
    if (genome_index == "") or (input_prefix == "None") or (output_prefix == "None"):
        print "Please check the pramater.\ngenome: " + genome_index + "\ninput: " + input_prefix + "\noutput_prefix:" + output_prefix
        if aligner == "BatMeth2":
            runprogram(abspath + "BatMeth2")
        sys.exit()
    if aligner == "BatMeth2":
        cmd = abspath + "batmeth2-align" + " -g " + genome_index + " -p " + str(threads) + " -n " + str(mismatches) + " -i " + input_prefix + " -o " + output_prefix + ".sam"
    elif aligner == "bwa-meth":
        cmd = "bwameth.py --reference " + genome_others + " " + input_prefix + " -t " + str(threads) + " --prefix " + output_prefix + ".sam"
    elif aligner == "bsmap":
        cmd = "bsmap -a " + input_prefix + " -d " + genome_index + " -o " + output_prefix + ".sam -p " + str(threads) + " -r " + 0
    elif aligner == "bismark2":
        cmd = "bismark " + os.path.dirname(genome_others) + " -U " + input_prefix + " --bowtie2 " + " -p " + str(threads) + " --prefix " + output_prefix + " --sam"
    elif aligner == "no":
        return
    else:
        print "Please select correct aligner. (BatMeth2/bwa-meth/bsmap/bismark2)"
    runprogram(cmd)

def alignmentPaired():
    if aligner == "no":
        return
    if (genome_index == "") or (input_prefix1 == "") or (output_prefix == "None") or (input_prefix2 == ""):
        print "Please check aligner pramaters.\ngenome: " + genome_index + "\ninput1: " + input_prefix1 + "\ninput2: " + input_prefix2 + "\noutput_prefix:" + output_prefix
        if aligner == "BatMeth2":
            runprogram(abspath + "BatMeth2")
        sys.exit()
    if aligner == "BatMeth2":
        cmd = abspath + "batmeth2-align" + " -g " + genome_index + " -p " + str(threads) + " -n " + str(mismatches) + " -i " + input_prefix1 + " -i " + input_prefix2 + " -o " + output_prefix + ".sam"
    elif aligner == "bwa-meth":
        cmd = "bwameth.py --reference " + genome_others + " " + input_prefix1 + " " + input_prefix2 + " -t " + str(threads) + " --prefix " + output_prefix + ".sam"
    elif aligner == "bsmap":
        cmd = "bsmap -a " + input_prefix1 + " -b " + input_prefix2 + " -d " + genome_index + " -o " + output_prefix + ".sam -p " + str(threads) ##+ " -r  0"
    elif aligner == "bismark2":
        cmd = "bismark " + os.path.dirname(genome_others) + " -1 " + input_prefix1 + " -2 " + input_prefix2 + " --bowtie2 " + " -p " + str(threads) + " --prefix " + output_prefix + " --sam"
    elif aligner == "no":
        return
    else:
        print "Please select correct aligner. (BatMeth2/bwa-meth/bsmap/bismark2)"
    runprogram(cmd)

def annoation():
    if gfffile == "None":
        return
    methratio = output_prefix + ".methratio.txt"
    if gfffile != "None":
        if GTF == "True":
            cmd = abspath + "methyGff" + " -o " + output_prefix + " -G " + genome_index + " -gtf " + gfffile + " -m " + methratio + " -B -P --TSS --TTS --GENE"
        else:
            cmd = abspath + "methyGff" + " -o " + output_prefix + " -G " + genome_index + " -gff " + gfffile + " -m " + methratio + " -B -P --TSS --TTS --GENE"
    elif bedfile != "None":
        cmd = abspath + "methyGff" + " -o " + output_prefix + " -G " + genome_index + " -b " + bedfile + " -m " + methratio + " -B -P --TSS --TTS --GENE"
    if step != 0.025:
        cmd = cmd + " -s " + step
    if chromstep != 50000:
        cmd = cmd + " -S " + chromstep
    if coverage != 5:
        cmd = cmd + " -c " + coverage
    if maxcoverage != 1000:
        cmd = cmd + " -C " + maxcoverage
    if binCover != 3:
        cmd = cmd + " -nC " + binCover
    if distance != 2000:
        cmd = cmd + " -d " + distance
    runprogram(cmd)

##methylation data visulization
def visulize():
    path1 = os.path.dirname(__file__)
    abspath = os.path.abspath(path1)

###get filenames contain outprefix
def IsSubString(SubStrList,Str):
    flag=True
    for substr in SubStrList: 
        if not(substr in Str): 
            flag=False
    return flag 
#~ #---------------------------------------------------------------------- 
def GetFileList(FindPath,FlagStr=[],containlocation=False):  
    FileList=[] 
    FileNames=os.listdir(FindPath) 
    if (len(FileNames)>0): 
        for fn in FileNames: 
            if (len(FlagStr)>0): 
            #return file names contain outprefix
                if (IsSubString(FlagStr,fn)):
                    if containlocation:
                        fullfilename=os.path.join(FindPath,fn) 
                        FileList.append(fullfilename)
                    else:
                        FileList.append(fn)
            else: 
            #otherwise return all files 
                if containlocation:
                    fullfilename=os.path.join(FindPath,fn)
                    FileList.append(fullfilename) 
                else:
                    FileList.append(fn)
    #sort file names
    if (len(FileList)>0): 
        FileList.sort() 
    return FileList

def printoutputfiles():
    FileList = []
    SubStrList = [output_prefix]
    containlocation = False
    FileList = GetFileList(workdir, SubStrList, containlocation)
    fouts = mkpath + "/images/outfiles.txt"
    Fouts = open(fouts, "w")
    file = "File_Name\tDirectory\n"
    Fouts.write(file)
    for file in FileList:
        file = file + "\t" + workdir + "\n" 
        Fouts.write(file)
    path = mkpath + "/images/"
    FileList = GetFileList(path, ["png"], containlocation)
    for file in FileList:
        file = file + "\t" + path + "\n" 
        Fouts.write(file)
    FileList = GetFileList(path, ["txt"], containlocation)
    for file in FileList:
        file = file + "\t" + path + "\n" 
        Fouts.write(file)

    FileList = GetFileList(mkpath, ["html"], containlocation)
    for file in FileList:
        file = file + "\t" + mkpath + "\n" 
        Fouts.write(file)
    Fouts.close()

def mvpng():
    FileList = []
    containlocation = False
    FileList = GetFileList(workdir, [output_prefix, "png"], containlocation)
    for file in FileList:
        oldpost = workdir + "/" + file
        newpost = mkpath + "/images/" + file.replace(output_prefix + ".",'')
        print "move file " + oldpost + " to " + newpost
        shutil.move(oldpost, newpost)

def doc2html():
    FileList = []
    containlocation = False
    path = mkpath + "/images/"
    FileList = GetFileList(path, "txt", containlocation)
    for file in FileList:
        print "convert " , file, " to html."
        cmd = "Rscript " + abspath + "doc2html.r " + workdir + " " + output_prefix + " " + file
        runprogram(cmd)

def alignmentstate():
    alignresults = output_prefix + ".alignresults.txt"
    Falignresults = open(alignresults, "w")
    Falignresults.write("Value\tState\n")
    Falignresults.close()
    alignsortbam = "samtools sort -@ " + str(threads) +" -o " + output_prefix + ".sort.bam " + output_prefix + ".sam"
    runprogram(alignsortbam)
    alignsummarycmd = "samtools flagstat -@ " + str(threads) + " " + output_prefix + ".sort.bam >> " + alignresults + " && tail -14 " + alignresults + " | sed 's/ /_/' | sed 's/ /_/' | sed 's/ /\\t/' | sed 's/_/ /g' > " + mkpath + "/images/alignresults.txt"
    runprogram(alignsummarycmd)

def mkreport():
    if output_prefix == "None":
        print "\nplease define -o outfileprefix.\n"
        sys.exit()
    copydir(oldreportdir, mkpath)
    printparamter1()
    printparamter2()
    alignmentstate()
    methratioLogfile = output_prefix + ".log.txt"
    newlogfile = mkpath + "/images/methratio.txt"
    shutil.copyfile(methratioLogfile,newlogfile) 
    mvpng()
    printoutputfiles()
    doc2html()

def methyPlot():
    ##
    cmd = abspath + "methyPlot " + output_prefix + ".methBins.txt " + output_prefix + ".Methygenome.pdf " + str(step) + " " +output_prefix + ".Methylevel.1.txt " + output_prefix + ".function.pdf TSS TTS " + output_prefix + ".AverMethylevel.1.txt " + output_prefix + ".Methenrich.pdf"
    ##cmd = "{output_prefix}.bins..."
    ##cmd = cmd.format(**locals())
    runprogram(cmd)
    cmd = "Rscript "+ abspath + "density_plot_with_methyl_oneSample_oneGff.r "+ output_prefix + ".methBins.txt " + output_prefix + ".annoDensity.1.txt " + output_prefix + ".density.pdf " + output_prefix
    ##cmd = cmd.format(**locals())
    runprogram(cmd)
    cmd = "Rscript " + abspath + "mCdensity.r " + output_prefix + ".mCdensity.txt " + output_prefix + ".mCdensity.pdf " + output_prefix + ".mCcatero.txt " + output_prefix + ".mCcatero.pdf"
    runprogram(cmd)
    cmd = abspath + "GeneMethHeatmap " + output_prefix + " None " + str(CG) + " " + str(CHG) + " " + str(CHH)
    runprogram(cmd)

def visul2sample():
    cmd = abspath + "GeneMethHeatmap {sample1_prefix} {sample2_prefix} {CG} {CHG} {CHG}"

def fastptrim():
    if fastp != "":
        if pairedend == "True":
            cmd = fastp + " -i " + 

## whole pipeline for DNA methylation analysis. Contains alignment, calute meth level, DNA methylation annatation
## on gff file or bed region, DNA methylation visulization. Differentail analysis use diffmeth function.
def runpipe():
    copydir(oldreportdir, mkpath)
    printparamter1()
    printparamter2()
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Alignment ..."
    align_result = output_prefix + ".sam"
    if pairedend == "True":
        alignmentPaired()
    else:
        alignmentSingle()
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Alignment summary ..."
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Sorting align file ..."
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] ", alignmentstate()
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Methylation Status ..."
    align_result = output_prefix + ".sort.bam"
    calmeth(genome_index, mismatches, align_result, output_prefix, threads)
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Annotation ..."
    annoation()
    methratioLogfile = output_prefix + ".log.txt"
    newlogfile = mkpath + "/images/methratio.txt"
    shutil.copyfile(methratioLogfile,newlogfile) 
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Visulization ..."
    methyPlot()
    mvpng()
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Output files ..."
    printoutputfiles()
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Make batmeth2 report ..."
    doc2html()
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Done!"
    print "[", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "] Please run differentail analysis ..."

#"pipel", "index", "align", "calmeth", "anno", "visul", "diffmeth", "visuldiff", DManno"

def detect_mode():
    command = sys.argv[1]
    para = ""
    if(command != "pipel"):
        for i in range(2, len(sys.argv)):
            para = para + " " + sys.argv[i]
    if command == "build_index":
        build_index(para)
    elif command == "pipel":
        runpipe()
    elif command == "align":
        if pairedend == "True":
            alignmentPaired()
        else:
            alignmentSingle()
    elif command == "calmeth":
        cmd = abspath + "calmeth " + para
        runprogram(cmd)
    elif command == "annoation":
        cmd = abspath + "methyGff " + para
        runprogram(cmd)
    elif command == "methyPlot":
        cmd = abspath + "methyPlot" + para
        runprogram(cmd)
    elif command == "batDMR":
        cmd = abspath + "batDMR" + para
        runprogram(cmd)
    elif command == "DMCplot":
        cmd = abspath + "DMCannotationPlot" + para
        runprogram(cmd)
    elif command == "visul2sample":
        visul2sample()
    elif command == "mkreport":
        mkreport()
    else:
        print "can not detect any command!"
        usage()
        sys.exit()

if len(sys.argv) < 4:
    if mode == "pipel":
        usage()
    else:
        detect_mode()
    sys.exit()

detect_mode()
