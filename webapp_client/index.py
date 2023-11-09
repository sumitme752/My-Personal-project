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
            padding: 8px;
            text-align: left;
            cursor: pointer;
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
                <span class="file_name_margin" style="font-weight: bold; color: black"> File List</span>
            </div>
        </div>
    </div>
    <div class="content_index">
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Questionnair</th>
                        <th>Proposed Answer</th>
                    </tr>
                </thead>
                <tbody id="fileDataBody">
                """
    for item in data_list:
        pdf_file = item[0]
        csv_file = item[1] if len(item) > 1 else ""
        table_html += f"""
            <tr>
                <td>{pdf_file}</td>
                <td class="csv_file_type">
                  <a href="/{csv_file}" >{csv_file}</a>
                </td>
            </tr>
            """

    table_html += """
            </table>
        </div>
    </div>
    <script>
        function bindDataToTable(file_name) {
            localStorage.setItem("jsonData", JSON.stringify({ file_name : file_name, json_list : answer_Data, }));
            window.location.href = "answer_details.html"
        }
    </script>
</body>
</html>
"""
    return table_html

data_list = [
    ("1.pdf", "1.csv"),
    ("2.pdf", "2.csv"),
    ("3.pdf", "3.csv"),
    ("4.pdf", "4.csv"),
]

html_table = generate_html_file_table(data_list)
# print(html_table)
def generate_html_file_answer_list(csv_file_name, answer_data_list):
    csv_name = csv_file_name
    html_table_answer_list = """
        <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title></title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
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


                    /* thead {
                        background-color: #f2f2f2;
                        position: sticky;
                        top: 0; 
                    } */
                    th, td {
                        border: 1px solid #ccc;
                        padding: 8px;
                        text-align: left;
                        cursor: pointer;
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
                        <div class="center"> """
    html_table_answer_list += f"""<span class="file_name_margin" id="file_name" style="color:black">{csv_name}</span>
                            <a href="/{csv_name}"><span style="color: black; cursor: pointer;" ><i class="fa fa-download"></i></span></a>
                        </div>
                    </div>
                </div>
                <div class="content_new">
                    <div class="table-container-details">
                    <form>
                        <table>
                            <thead>
                            </thead>
                            <tbody id="tableBody">
                                <form action="details.html" method="post">
                                """
    for item in answer_data_list:
        question = item[0]
        answer = item[1] if len(item) > 1 else ""
        html_table_answer_list += f""" 
                            <tr>
                                <td style="width: 3%;"><i class="fas fa-trash"></i></td>
                                <td style="width: 47%;">
                                    {question}
                                </td>
                                <td style="width: 50%;">
                                    <input type="text" value="{answer}">
                                </td>
                                </tr>
                            """

    html_table_answer_list += """
            </tbody>
        </table>
        <div class="row">
            <div class="col-50"></div>
            <div class="col-50 mt-15">
                <button type="submit" id="download">save</button>
            </div>
        </div>
        </form>
    </div>
</div>
</body>
</html>
"""
    return html_table_answer_list


answer_Data = [
    ("How many shares are allocated to this Unit?", 385),
    ("Exact name of current owners of shares per your records?", "MARTIN LAMB"),
    ("When does the proprietary lease expire?", "09/30/2100"),
    (
        "What is the cash on hand/reserve fund as of today? ",
        "Reserve $3,496,080.11\r\nCAsh $34,383.20",
    ),
    (
        "Are there any other large expenses due that have not been paid yet by the corporation? ",
        "No",
    ),
    (
        "Does the building have a mortgage? If so, what is the principal amount, interest rate, and maturity date? Lender?",
        " $10,000,000 Interest Rate: 4.24% \r\nMaturity Date:11/30/2028",
    ),
    (
        "Does the building have a credit line? If so, what is the original amount and how much has been drawn down?",
        "Balance: $2,000,000Fixed Rate: 2.25%",
    ),
    ("Are there any major maintenance arrearages?", ""),
    (
        "Is there any pending litigation where the Corporation is a \r\ndefendant or plaintiff? \r\no If so, please provide index number:\r\no Current state of the litigation:\r\no Amount of damages being sought:\r\no Is the claim covered by insurance?\r\no If settled or lost at trial, how will the damages be \r\npaid?\r\no Is the action covered by the building’s insurance?\r\no Approximate settlement/trial date:",
        "No",
    ),
    ("What is the current maintenance for this Unit", ""),
]
file_name = "10park.csv"
generate_html_answer_table = generate_html_file_answer_list(file_name, answer_Data)
print(generate_html_answer_table)
