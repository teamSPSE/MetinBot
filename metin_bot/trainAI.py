from utils.samples import generate_negative_description_file

generate_negative_description_file('classifier/samples/all/negative')

# cd C:\Virtuals\MCxMeTiNcze\Metin2-Bot\metin_bot
# C:\Virtuals\MCxMeTiNcze\opencv\build\x64\vc15\bin\opencv_annotation.exe --annotation=pos.txt --images=classifier/samples/all/positive_new
# C:\Virtuals\MCxMeTiNcze\opencv\build\x64\vc15\bin\opencv_createsamples.exe -info pos.txt -w 45 -h 45 -num 2000 -vec pos.vec
# C:\Virtuals\MCxMeTiNcze\opencv\build\x64\vc15\bin\opencv_traincascade.exe -data classifier/cascadeMetinAll/cascade/ -vec classifier/samples/all/pos.vec -bg classifier/samples/all/neg.txt -w 45 -h 45 -numPos 1600 -numNeg 3000 -numStages 10 -numThreads 24 -acceptanceRatioBreakValue 0.0001