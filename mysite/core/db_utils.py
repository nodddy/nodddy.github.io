import pdfkit
import pandas as pd

WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
PDF_OPTIONS = {
    'margin-top': '0.1in',
    'margin-right': '0.1in',
    'margin-bottom': '0.1in',
    'margin-left': '0.1in',
    'minimum-font-size': 18,
    'encoding': "UTF-8"
}
PD_HTML_BASE = '<html>' \
               '<meta charset="utf-8">' \
               '<meta name="viewport" content="width=device-width, initial-scale=1">' \
               '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"' \
               ' rel="stylesheet"integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6"' \
               ' crossorigin="anonymous">' \
               '<body> {table} </body>' \
               '</html>'  # bootstrap CSS is loaded from website


def convert_csv_to_pdf(instance, file_name, file):
    """
    Gets the csv attribute from file model and then converts it in form of a JSON string
    to a pandas dataframe and then html with specified CSS in 'PD_HTML_BASE.
    Finally the html gets converted to pdf and saved to the file_instance path with .pdf added.
    :param file_instance: the input_instance of file model
    :return: A string with the pdf file path
    """

    instance.csv = csv_to_json(file, instance.file_delimiter)
    pd.set_option('colheader_justify', 'center')
    json_to_pdf(instance.csv, f'{instance.absolute_path(file_name)}.pdf')
    return f'{instance.upload_folder}{file_name}.pdf'


def json_to_pdf(json_str, output_path):
    df_html = PD_HTML_BASE.format(table=pd.read_json(json_str).to_html(na_rep='', classes='table'))
    create_pdf(df_html, output_path)
    return


def csv_to_json(file, delimiter):
    def reduce_df(df: pd.DataFrame):
        if (df_length := len(df)) > 10000:
            return df.iloc[::20]
        elif df_length > 1000:
            return df.iloc[::10]
        elif df_length > 100:
            return df.iloc[::2]
        else:
            return df

    dataframe = pd.read_csv(file, delimiter)
    reduced_dataframe = reduce_df(dataframe)
    json_str = reduced_dataframe.to_json()
    return json_str


def txt_to_pdf(input_instance, input_file_name):
    """
    Takes file_instance and generates a pdf file from the txt file, then saves it to the file_instance's
    path with .pdf added.
    :return: A string with the pdf file path
    """
    file = input_instance.file._file.read().decode('utf-8')
    output_path = f'{input_instance.absolute_path(input_file_name)}.pdf'
    create_pdf(file, output_path)
    return f'{input_instance.upload_folder}{input_file_name}.pdf'


def create_pdf(file_or_path, output_path):
    pdfkit.from_string(
        file_or_path, output_path,
        configuration=PDF_CONFIG, options=PDF_OPTIONS
    )
    return
