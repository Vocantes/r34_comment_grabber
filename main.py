import pandas as pd
import requests
from bs4 import BeautifulSoup
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import random


app = dash.Dash(__name__)


app.layout = html.Div(style={'backgroundColor': 'black', 'padding': '40px', 'margin': '0', 'height': '100%', 'width': '100%'},
    children=[
        html.H1("Rule 34 Comment Grabber", style={'textAlign': 'center', 'color': 'white',
                                               'font-size': 40}),

                                               html.Div(dcc.Input(id="Tags",type="text",n_submit=0,value='',
                                               placeholder="Tags Seperated by commas"),
                                               style={"textAlign":"center","color":"black"}),

                                               html.Div(html.Img(id="Image",src="/assets/owo.jpg"),style={"textAlign":"center"}),

                                               html.Div(dcc.Slider(0,10,1, value=1,id="slider")),

                                              html.H2("Comments", id="comments_heading",style={"textAlign":"center","font-size":"35","color":"white"}),
                                              html.Div(html.Pre(id="comments",children=[]),style={"textAlign":"center", "color":"white","font-size":25}),
                                              dcc.Store(id="data-store",storage_type="session",data=[]),
                                              dcc.Store(id="comment-data",storage_type="session",data=[])
                                          ]
)

@app.callback(
    [Output("data-store","data")],
    [Input("Tags","n_submit")],
    [State("Tags","value")],
    prevent_initial_call=True
)

def get_r34_data(n,Tags):
    if n > 0:
        Tags = list(str(Tags).strip().split(","))
        payload = {"json":1,"tags":Tags}
        result = requests.get("https://api.rule34.xxx/index.php?page=dapi&s=post&q=index",payload)
        data = pd.read_json(result.text)
        data = data[data["comment_count"] > 0]
        indexes= []
        #FIX LEN(DATA) , 11 PART
        if len(data) < 11:
            indexes.extend(list(range(0,len(data))))
        else:
            while len(indexes) < 11:
                ind = random.randint(0,len(data) - 1)
                if ind not in indexes:
                    indexes.append(ind)
        data = data.iloc[indexes]
        data.reset_index(inplace=True)
        data = data.to_dict()
        data = [data]
        return data

@app.callback(
    [Output("Image","src"), Output("comment-data","data")],
    [Input("data-store","data"),Input("slider","value")]
)
def get_img_and_comments(data_store,slider_val):
    data_dict = data_store
    data = pd.DataFrame(data_dict)
    if slider_val >= len(data):
        return dash.no_update, dash.no_update
    data = data.iloc[int(slider_val)]
    post_id = str(data["id"])
    print(post_id)
    com_payload = {"post_id":[post_id]}
    comment_url = "https://api.rule34.xxx/index.php?page=dapi&s=comment&q=index"
    comment_req = requests.get(comment_url, com_payload)
    soup = BeautifulSoup(comment_req.content,features="xml")
    
    comment_dict = {"comment body": [],
                    "created_at": [],
                    "creator":[],
                    "creator_id":[],
                    "id": [],
                    "post_id":[]
                }

    for i,j in enumerate(soup.findChildren("comment")):
        comment_dict["comment body"].append(str(j).split("comment body=")[1].split("created_at=")[0].strip())
        comment_dict["created_at"].append(str(j).split("created_at=")[1].split("creator=")[0].strip())
        comment_dict["creator"].append(str(j).split("creator=")[1].split("creator_id=")[0].strip())
        comment_dict["creator_id"].append(str(j).split("creator_id=")[1].split("id=")[0].strip())
        comment_dict["id"].append(str(j).split("id=")[1].split("post_id")[0].strip())
        comment_dict["post_id"].append(str(j).split("post_id")[1].split('"')[1])
    image_url = data["sample_url"]
    return image_url, [comment_dict]

@app.callback(
    [Output("comments","children")],
    [Input("comment-data","data")]
)

def update_comments(comment_data):
    comment_df = pd.DataFrame(comment_data[0])
    comment_list = []
    for i in range(len(comment_df)):
        row = comment_df.iloc[i]
        body = row["comment body"]
        date = row["created_at"]
        creator = row["creator"]

    
    
        string = body + " User- " + creator + " Date-" + date
        comment_list.append(string)
    mystring = "\n".join(comment_list)
    return [mystring]





if __name__ == "__main__":
    app.run()