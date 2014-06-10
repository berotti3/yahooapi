#coding:utf-8
import json
import urllib2
import urllib
import sys
import os

appid = "ここにappidを入れる"
yahooUrl = "http://shopping.yahooapis.jp/ShoppingWebService/V1/json/"

reviewUrl = "reviewSearch?"
categoryUrl = "categorySearch?"

"""
指定されたidのカテゴリのレビュー文を取得
入力：カテゴリid,開始番号
出力：辞書型で50件分のデータ
"""
def getReview(category_id,start_num):
    params = urllib.urlencode(
        {'appid': appid,
        'category_id':category_id,
        'results':50,
        'start':start_num*50+1})
    url = yahooUrl + reviewUrl + params
    response = urllib2.urlopen(url).read()
    return json.loads(response)

"""
指定されたカテゴリidの子カテゴリ一覧を取得
入力：親カテゴリのid
出力：辞書型で子カテゴリ一覧
"""
def getCategory(num):
    params = urllib.urlencode(
        {'appid': appid,
        'category_id':num})
    url = yahooUrl + categoryUrl + params
    response = urllib2.urlopen(url).read()
    return json.loads(response)

"""
入力：なし
出力：一番上の層のカテゴリのリスト[[id,名前],[id,名前],,]
"""
def makeCategoryList():
    #category["ResultSet"]["0"]["Result"]["Categories"]["Children"][キー]["Id"]に子のIDが入っている
    categoryList = []
    category = getCategory(1)
    child_list = category["ResultSet"]["0"]["Result"]["Categories"]["Children"]
    for key in child_list.keys():
        tmplist = []
        try:
            tmplist.append(child_list[key]["Id"])
            tmplist.append(child_list[key]["Title"]["Short"].encode("utf-8"))
            categoryList.append(tmplist)
        except TypeError:
            sys.stderr.write("TypeError\n")            
    return categoryList

"""
入力：カテゴリの[[id,名前],[id,名前],,]リスト,　レビュー取得件数
出力： [[[id,カテゴリ名],[[文num,文],[文num,文]]],,,]
"""    
def makeReviewList(category_lists, review_num):
    review_lists = []
    for category in category_lists:
        review_list = []
        review = []
        i=0
        category_id = category[0]#0がid,1が名前
        #指定した数レビューを取ってくる
        for j in range(1, review_num+1):
            review += getReview(category_id,j)["ResultSet"]["Result"]                    
        try:
            for review_data in review:
                i+=1
                num_review = [i, review_data["ReviewTitle"].encode("utf-8"),review_data["Description"].encode("utf-8")]
                review_list.append(num_review)
        except TypeError:
            sys.stderr.write("TypeErrors\n")
        category_reviewlist = [category, review_list]
        review_lists.append(category_reviewlist)
    return review_lists

"""
与えられたレビューのリストをファイルに出力
入力：[[[id,カテゴリ名],[[文num,文],[文num,文]]],,,] 
number:レビュー番号を出力するかどうかのbool
title:タイトルも出力するかどうかのbool
出力：なし
"""
def makeReviewFile(category_review_lists, number, title):
    for category_review_list in category_review_lists:
        #書き出し先のファイルを指定
        filename = str(category_review_list[0][0]) + "_" + category_review_list[0][1] +".txt"
        f = open(filename, "a+")
        write_cell = ""
        for num_review in category_review_list[1]:
            if number:
                write_cell += "number = " +str(num_review[0]) + "\n"
            if title:
                write_cell += "title : " + num_review[1] + "\n"
            write_cell +=  num_review[2] + "\n"
        f.write(write_cell)      
        f.close()
            
def main():
    #オプション取得設定　-nに入れた数*50のレビューを取ってくる
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-n", dest="n", type="int", help="取得するレビューの数/50,デフォルト=", default=1)
    #TrueFalseで入力
    parser.add_option("--number", dest="number", action="store_true", help="レビューの番号も出力するかどうか", default=False)
    parser.add_option("--title", dest="title", action="store_true", help="タイトルも出力するかどうか", default=False)
    (options, args) = parser.parse_args()
    
    #一番上の層のカテゴリのリスト
    categorylist = makeCategoryList()
 
    review_lists = makeReviewList(categorylist, options.n)#[[カテゴリごとの文,文],[カテゴリごとの文、文]]
    
    #カテゴリごとにファイルで出力
    makeReviewFile(review_lists, options.number, options.title)

if __name__ == "__main__":
    main()