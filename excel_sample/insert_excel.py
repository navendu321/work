import urllib
import urllib2
import xlsxwriter
import json




def insert_excel():

    url ="http://food2fork.com/api/search"
    query_args = {"key": "e1254d39d79328ef647ae25737895fe8",
                  "page": 33}

    encoded_args = urllib.urlencode(query_args)
    complete_url = url + "?" + encoded_args
    resp = urllib2.urlopen(complete_url)
    data = json.load(resp)


    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook('demo.xlsx')
    worksheet = workbook.add_worksheet()

    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 30)
    worksheet.set_column('F:F', 30)
    worksheet.set_column('G:G', 30)
    worksheet.set_column('H:H', 30)


    worksheet.write(0, 0, "PUBLISHER")
    worksheet.write(0, 1, "F2F URL")
    worksheet.write(0, 2, "TITLE")
    worksheet.write(0, 3, "SOURCE URL")
    worksheet.write(0, 4, "RECIPE ID")
    worksheet.write(0, 5, "IMAGE URL")
    worksheet.write(0, 6, "SOCIAL RANK")
    worksheet.write(0, 7, "PUBLISHER URL")


    
    row = 1
    for i in data['recipes']:
        worksheet.write(row, 0, i.get("publisher", ""))
        worksheet.write(row, 1, i.get("f2f_url", ""))
        worksheet.write(row, 2, i.get("title", ""))
        worksheet.write(row, 3, i.get("source_url", ""))
        worksheet.write(row, 4, i.get("recipe_id", ""))
        worksheet.write(row, 5, i.get("image_url", ""))
        worksheet.write(row, 6, i.get("social_rank", ""))
        worksheet.write(row, 7, i.get("publisher_url", ""))
        row += 1

    workbook.close()



if __name__ == "__main__":
    insert_excel()
