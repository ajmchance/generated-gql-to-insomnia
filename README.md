# generated-gql-to-insomnia
Pull generated gql queries into a insomnia-importable file

options:
-p / --path : path to the generated gql directory
-o / --out : path to the output file
-s / --secret : secret key to be put in every query
-n / --name : name of the insomnia request collection
-u / --url : default url

example usage :
`python gql-ripper.py -p mystuff/__generated__/ -o out/InsomniaConverted.json -n MyStuff_Queries -s MY_SECRET_KEY -u localhost:3000`
