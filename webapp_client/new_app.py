from flask import Flask, render_template, request, send_from_directory, redirect, send_file
import os
from urllib.parse import unquote
import csv
import glob
from datetime import datetime

app = Flask(__name__)

# Set the directory you want to list and serve files from
file_directory = "/Users/sumitkumar/Desktop/sumit_dir/Project_17_oct_23/vivek_sir_work/sample_csv_pdf"
app.config["file_directory"] = file_directory

PDF_FOLDER = os.path.join(app.root_path, "pdf_files")
app.config["PDF_FOLDER"] = PDF_FOLDER

# Set the directory for CSV files
CSV_FOLDER = os.path.join(app.root_path, "csv_files")
app.config["CSV_FOLDER"] = CSV_FOLDER


def generate_html_file_table(data_list):
    table_html = """                                
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>File Data</title>
    </head>
    <style>
        /* For details page css */
            /* CSS styles go here */
            body {
                font-family: Arial, sans-serif;
            }

            body, html {
                margin: 0;
                padding: 0;
                height: 100%;
            }

            table {
                border-collapse: collapse;
                width: 100%;
            }

            .table-container {
                margin-top: 40px;
            }

            .table-container-details {
                max-height: 400px; /* Adjust the maximum height as needed */
                overflow-y: auto; /* Enable vertical scrolling */
                
            }

            /* thead {
                background-color: #f2f2f2;
                position: sticky;
                top: 0; 
            } */
            th, td {
                border: 1px solid #ccc;
                padding: 5px;
                text-align: left;
            }

            th {
                background-color: #f2f2f2;
            }

            td.editable {
                cursor: pointer;
            }

            .center {
                text-align: center;
            }

            button {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 6px 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                border-radius: 6px;
                border: none;

                color: #fff;
                background: linear-gradient(180deg, #4B91F7 0%, #367AF6 100%);
                background-origin: border-box;
                box-shadow: 0px 0.5px 1.5px rgba(54, 122, 246, 0.25), inset 0px 0.8px 0px -0.25px rgba(255, 255, 255, 0.2);
                user-select: none;
                -webkit-user-select: none;
                touch-action: manipulation;
                cursor: pointer;
            }

            .row {
                display: flex;
            }
            .col-100 {
                width: 100%;
            }
            .col-50 {
                width: 50%;
            }
            .col-25 {
                width: 25%;
            }
            .col-10 {
                width: 10%;
            }

            .mt-30 {
                margin-top: 30px;
            }
            .mt-20 {
                margin-top: 20px;
            }
            .mt-15 {
                margin-top: 15px;
            }
            .mt12 {
                margin-top: px;
            }

            .padding-body {
                padding-left: 30px;
                padding-right: 30px;
            }

            .content {
                padding: 20px;
                /* margin-top: 10px; Adjust to accommodate the header height */
                /* You can add more styles here for your main content */
            }
            .content_index{
                margin-top: 60px;
            }

            .content_details {
                padding: 20px;
                margin-top: 50px; /* Adjust to accommodate the header height */
                /* You can add more styles here for your main content */
            }
            .content_new {
                padding: 20px;
                margin-top: 30px;  /*Adjust to accommodate the header height */
                /* You can add more styles here for your main content */
            }

            .header {
                background-color: #e8e8e8; /* Background color of the header */
                color: white; /* Text color of the header */
                padding: 10px; /* Adjust padding as needed */
                position: fixed; /* Fixed positioning */
                top: 0; /* Stick it to the top */
                width: 100%; /* Full width */
            }

            .footer {
                background-color: #e8e8e8;/* Background color of the footer */
                color: rgb(25, 22, 22); /* Text color of the footer */
                padding: 10px;  /*Adjust padding as needed */
                position: fixed; /* Fixed positioning */
                bottom: 0; /* Stick it to the bottom */
                width: 100%; /* Full width */
                margin-left: 0px !important;
            }
        
            


            /* for index page css */
        
            .center {
                text-align: center;
            }
            .file_name_margin {
                margin-top: -5px;
                font-size: 27px;
            }
            .circle {
                width: 40px; /* Adjust the circle size as needed */
                height: 40px; /* Same as width to create a circle */
                background-color: #007bff; /* Circle background color */
                border-radius: 50%; /* Make it a circle */
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* Style the Font Awesome icon inside the circle */
            .circle i {
                font-size: 24px; /* Adjust the icon size as needed */
                color: white; /* Icon color */
            }

            .csv_file_type{
                color: blue;
                text-decoration: underline;
            }
</style>
<body>
    <div class="row header">
        <div class="col-100">
            <div class="center">
                <span class="file_name_margin" style="font-weight: bold; color: black"> AKAM Queries</span>
            </div>
        </div>
    </div>
    <div class="content_index">
        <div class="table-container">
            <table>
                <thead>
                    
                </thead>
                <tbody id="fileDataBody">
                """
    for item in data_list:
        pdf_file = item[0][0]
        pdf_file_timestamp = item[0][1]
        csv_file = item[1][0] if len(item) > 1 else ""
        csv_file_timestamp = item[1][1] if len(item) > 1 else ""
        table_html += f"""
            <tr>
                <td style="font-size :large">{pdf_file}<br><span style="font-size : 11px; color:grey">{pdf_file_timestamp}</span></td>
                <td style="font-size :large">
                  <a href="http://127.0.0.1:5000/files/{csv_file}">{csv_file}</a><br><span style="font-size : 11px; color:grey">{csv_file_timestamp}</span>
                </td>
            </tr>
            """

    table_html += """
            </table>
        </div>
    </div>
</body>
</html>
"""
    return table_html


def generate_html_file_answer_list(csv_file_name, answer_data_list):
    csv_name = csv_file_name
    html_table_answer_list = """
        <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title></title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            </head>
            <style>
                /* For details page css */
                    /* CSS styles go here */
                    body {
                        font-family: Arial, sans-serif;
                    }

                    body, html {
                        margin: 0;
                        padding: 0;
                        height: 100%;
                    }
                    
                    table {
                        border-collapse: collapse;
                        width: 100%;
                    }

                    .table-container {
                        margin-top: 40px;
                    }
                    .table-container-details {
                        margin-top: 60px;
                    }
                    .border-red {
                        border-color : red !important;
                        outline: red;
                        border-top-style: solid;
                        border-left-style: solid;
                        border-radius : 5px
                    }

                    /* thead {
                        background-color: #f2f2f2;
                        position: sticky;
                        top: 0; 
                    } */
                    th, td {
                        border: 1px solid #ccc;
                        padding: 8px;
                        text-align: left;
                    }

                    th {
                        background-color: #f2f2f2;
                    }

                    td.editable {
                        cursor: pointer;
                    }

                    .center {
                        text-align: center;
                    }

                    button {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 6px 14px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                        border-radius: 6px;
                        border: none;

                        color: #fff;
                        background: linear-gradient(180deg, #4B91F7 0%, #367AF6 100%);
                        background-origin: border-box;
                        box-shadow: 0px 0.5px 1.5px rgba(54, 122, 246, 0.25), inset 0px 0.8px 0px -0.25px rgba(255, 255, 255, 0.2);
                        user-select: none;
                        -webkit-user-select: none;
                        touch-action: manipulation;
                        cursor: pointer;
                    }

                    .row {
                        display: flex;
                    }
                    .col-100 {
                        width: 100%;
                    }
                    .col-75 {
                        width: 75%;
                    }
                    .col-50 {
                        width: 50%;
                    }
                    .col-25 {
                        width: 25%;
                    }
                    .col-10 {
                        width: 10%;
                    }

                    .mt-30 {
                        margin-top: 30px;
                    }
                    .mt-20 {
                        margin-top: 20px;
                    }
                    .mt-15 {
                        margin-top: 15px;
                    }
                    .mt12 {
                        margin-top: px;
                    }

                    .padding-body {
                        padding-left: 30px;
                        padding-right: 30px;
                    }

                    .content {
                        padding: 20px;
                        /* margin-top: 10px; Adjust to accommodate the header height */
                        /* You can add more styles here for your main content */
                    }
                    .content_index{
                        margin-top: 60px;
                    }
                    .content_details {
                        /* padding: 20px; */
                        margin-top: 70px; /* Adjust to accommodate the header height */
                        /* You can add more styles here for your main content */
                    }
                    .content_new {
                        /* padding: 20px; */
                        /* You can add more styles here for your main content */
                    }

                    .header {
                        background-color: #e8e8e8; /* Background color of the header */
                        color: white; /* Text color of the header */
                        padding: 10px; /* Adjust padding as needed */
                        position: fixed; /* Fixed positioning */
                        top: 0; /* Stick it to the top */
                        width: 100%; /* Full width */
                        z-index: 9999;
                    }

                    .footer {
                        background-color: #e8e8e8;/* Background color of the footer */
                        color: rgb(25, 22, 22); /* Text color of the footer */
                        padding: 10px;  /*Adjust padding as needed */
                        position: fixed; /* Fixed positioning */
                        bottom: 0; /* Stick it to the bottom */
                        width: 100%; /* Full width */
                        margin-left: 0px !important;
                    }
                


                    /* for index page css */
                
                    .center {
                        text-align: center;
                    }
                    .file_name_margin {
                        margin-top: -5px;
                        font-size: 27px;
                    }
                    .circle {
                        width: 40px; /* Adjust the circle size as needed */
                        height: 40px; /* Same as width to create a circle */
                        background-color: #007bff; /* Circle background color */
                        border-radius: 50%; /* Make it a circle */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    
                    /* Style the Font Awesome icon inside the circle */
                    .circle i {
                        font-size: 24px; /* Adjust the icon size as needed */
                        color: white; /* Icon color */
                    }

                    .csv_file_type{
                        color: blue;
                        text-decoration: underline;
                    }

                    .hover-container {
                        position: relative;
                        display: inline-block;
                    }

                    .hover-info {
                        display: none;
                        position: absolute;
                        top: 100%;
                        left: 0;
                        background-color: #fff;
                        border: 1px solid #ccc;
                        padding: 10px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                        z-index: 1;
                        width: 150px;
                        border-radius: 5px;
                    }

                    .hover-trigger:hover + .hover-info {
                        display: block;
                    }
                    .circle-hyphen {
                        display: inline-block;
                        position: relative;
                        width: 20px; /* Adjust the width and height as needed */
                        height: 20px;
                    }

                    .hyphen {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        font-size: 24px; /* Adjust the font size as needed */
                        color: #333; /* Adjust the color as needed */
                        border: 2px solid #333; /* Adjust the border color and thickness as needed */
                        border-radius: 50%;
                        width: 100%;
                        height: 100%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
            </style>
            <body>
                <div class="row header">
                    <div class="col-100">
                        <div class="center"> """
    html_table_answer_list += f"""<span class="file_name_margin" id="file_name" style="color:black">{csv_name}</span>&nbsp;&nbsp;
                            <a href="http://127.0.0.1:5000/files/download/{csv_name}" id="download_link"><span style="color: black; cursor: pointer;" ><i class="fa-solid fa-download"></i></span></a>
                        </div>
                    </div>
                </div>
                <div class="content_new">
                    <div class="table-container-details">
                    <form id="questionnair_form" action="http://127.0.0.1:5000/files/save/{csv_name}" method="POST">
                        <table>
                            <thead>
                            </thead>
                            <tbody id="tableBody">
                                """
    for index,item in enumerate(answer_data_list):
        question = item[0]
        answer = item[1] if len(item) > 1 else ""
        confidence = item[2] if len(item)> 2 else ""
        html_table_answer_list += f""" 
                            <tr>
                                <td style="width: 3%;">
                                    <div class="hover-container" onclick="deleteRow(this)">
                                        <div class="hover-trigger"><span style="cursor: pointer;"><i class="fa-solid fa-circle-minus"></i></span></div>
                                        <div class="hover-info" style="color:red">If this question is not relevant to you, you can simply click to delete it</div>
                                    </div>
                                </td>
                                <td style="width: 47%;">
                                    {question}
                                </td>
                                <input type="hidden" name="question_{index}" value="{question}">
                                <td style="width: 25%;">
                                    <input type="text" name="answer_{index}" value="{answer}" oninput="change_boder_color(event)" style="width:70%">
                                </td>
                                 <td style="width: 25%;">
                                    {confidence}
                                </td>
                                <input type="hidden" name="confidence_{index}" value="{confidence}">
                                </tr>
                            """

    html_table_answer_list += """
                            </tbody>
                        </table>
                        <div class="row">
                            <div class="col-50"></div>
                            <div class="col-50 mt-15" style="margin-bottom : 10px">
                                <button type="submit" id="download">save</button>
                            </div>
                        </div>
                    </form>
                </div>
</div>
<script>
    function deleteRow(button) {
        var row = button.parentNode.parentNode;
        row.parentNode.removeChild(row);
    }

    function change_boder_color(e) {
        let targetElement = e.target;
            targetElement.classList.add("border-red"); 
    }

    let skip_pressed = false;
    function checkEscKey(event) {
        let skip_key_pressed = (event.key === 'Escape' || event.key === 'Esc' && !skip_pressed)
        if (event.key === 'Escape' || event.key === 'Esc' && !skip_pressed) {
            document.activeElement.blur();
            document.body.focus()
            skip_pressed = true
        }
        if(skip_pressed && event.key === 'd' || event.key === 'D'){
                document.getElementById('download_link').focus()
                //document.getElementById('download_link').click();
            skip_pressed = false
        }
        if(skip_pressed && event.key === 's' || event.key === 'S'){
            document.getElementById('download').focus()
            //document.getElementById('questionnair_form').submit();
            skip_pressed = false
        }
    }
    document.addEventListener('keydown', checkEscKey);
    
</script>
</body>
</html>
"""
    return html_table_answer_list


@app.route("/files")
def files_list():
    file_list = os.listdir(file_directory)
    
    pdf_file_list = [file for file in file_list if file.endswith(".pdf")]
    csv_files_list = [file for file in file_list if file.endswith(".csv")]

    pdf_file_names = [file for file in pdf_file_list if not file.startswith("~$")]
    csv_file_names = [file for file in csv_files_list if not file.startswith("~$")]

    tuple_list = []
    for pdf in pdf_file_names:
        pdf_path = os.path.join(file_directory, pdf)
        pdf_timestamp = datetime.fromtimestamp(os.path.getmtime(pdf_path)).strftime('%b %d, %Y %I:%M:%S%p')
        csv_file = next((csv for csv in csv_file_names if pdf.split(".")[0] in csv), "")
        if csv_file:
            csv_path = os.path.join(file_directory, csv_file)
            csv_timestamp = datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime('%b %d, %Y %I:%M:%S%p')
            tuple_list.append(((pdf, pdf_timestamp), (csv_file, csv_timestamp)))
        else:
            tuple_list.append(((pdf, pdf_timestamp), ("", "")))

    generated_file_list = generate_html_file_table(tuple_list)
    return generated_file_list


@app.route("/files/<file_name>")
def csv_file_read(file_name: str)-> str:
    csv_files = glob.glob(os.path.join(file_directory, "*.csv"))
    file_in_directory = file_name in [os.path.basename(file) for file in csv_files]
    if file_in_directory:
        csv_file_directory = file_directory + "/" + file_name
        with open(csv_file_directory, mode="r") as file:
            csv_reader = csv.reader(file)
            csv_tuple_list = []
            for row in csv_reader:
                csv_tuple_list.append(tuple(row))
            return generate_html_file_answer_list(file_name, csv_tuple_list)
    else:
        print(f"CSV file '{file_name}' not found in the folder.")
        return (f"CSV file '{file_name}' not found in the folder.")
    


@app.route("/files/save/<file_name>", methods=['POST'])
def update_csv_file(file_name: str)-> str:
    request_type = request.method == 'POST'
    if request_type:
        question_answers = []
        index = 0
        while True:
            data = request.form
            question_key = f'question_{index}'
            answer_key = f'answer_{index}'
            confidence_key = f'confidence_{index}'
            # Check if the fields exist in the form data
            if question_key in data and answer_key in data and confidence_key in data:
                question = data[question_key]
                answer = data[answer_key]
                confidence = data[confidence_key]
                question_answers.append((question, answer, confidence))
                print(question)
            else:
                if index >= len(data):
                    break
            
            index += 1
        csv_file_directory = file_directory + '/'+ file_name
        with open(csv_file_directory, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(question_answers)

        return generate_html_file_answer_list(file_name, question_answers)
    else:
        return "<div style='text-align:center; margin-top:20%'> Failed to update this file Go to <a href='http://127.0.0.1:5000/files'>home</a></div>" 


@app.route("/files/download/<file_name>")
def download_csv_file(file_name: str)-> str:
    csv_files_list = glob.glob(os.path.join(file_directory, "*.csv"))
    file_name_in_directory = file_name in [os.path.basename(file) for file in csv_files_list]
    if file_name_in_directory:
        found_csv_file_name = file_directory + "/" + file_name        
        return send_file(found_csv_file_name, as_attachment=True)
    else:
        return (f"CSV file '{file_name}' not found in the folder.")

if __name__ == "__main__":
    app.run(debug=True)
