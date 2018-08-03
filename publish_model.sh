model=$1
tar zcvf $model.tgz $model
chmod a+r $model
scp $model.tgz bionlp-www.utu.fi:/var/www/bionlp-www/dep-parser-models
