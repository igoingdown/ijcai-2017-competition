# The source files of my IJCAI-2017 Competition.

## Dataset
*Because user_pay.txt, user_view.txt and extra_user_view.txt are bigger than 100MB, 
it can't be pushed onto github, just look at the **Get dataset** part.*
* __shop_info.txt__: Shop's information.
* __user_pay.txt__: User's pay history.
* __user_view.txt__: User's view history.
* __extra_user_view.txt__:A padding to the original user's view History.

## Get dataset:
* [user_pay.txt, and user_view.txt and extra_user_view.txt](https://tianchi.aliyun.com/competition/information.htm?raceId=231591)

## Task
According to Users' history data and shops' information, 
predict users' pay behavior int he next 2 weeks.

## Result
We designed 5 models. the SVM model bring us our top score: `539/4058`. 

And the prediction loss on the dev set of every model is:
* LR: `0.00553571428571`
* SVM: `0.00107142857143`
* KNN: `0.0166071428571`
* GBDT: `0.169285714286`
* RF: `0.0301785714286`

