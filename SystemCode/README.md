# follow the step to start the apps.
1. download the link from the onedrive by using nus account: https://nusu-my.sharepoint.com/:f:/g/personal/e0687370_u_nus_edu/EgWtcxkf8_5GuvQKga8amzYBDQ0ugH6AlhIOFsB8gCOPCQ?e=faTrZN
2. Create a virtualenv
3. Manually install Django and other dependencies through `pip install -r requirements.txt`
4. Unzip the sourceCode zip file and go to the directory "sourceCode/PLPPM"
5. copy the folders "gql" "intention" "investopedia" and "sql" and place inside the folder "sourceCode/PLPPM"
6. run text2GQL/text2GQL_training.ipynb file to load the data into Neo4j server.
7. change the neo4j database username and password under "sourceCode/PLPPM/gql/gql.py"
8. run django command python manage.py runserver

