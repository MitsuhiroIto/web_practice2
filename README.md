# web_practice2
AWS Batchのjobを設定する  
AWS Batchのdocker上でGPUを使いたい場合はこちら
https://qiita.com/MitsuhiroIto/private/3d59797e8f4700339993
 ```
python create-batch-entities.py --compute-environment <job名>
 ```
deployする(ローカル)
```
python python app.py
```
deployする(AWS)
```
zappa deploy
```
