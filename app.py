import base64

import pandasdmx as sdmx
import pandas as pd
import streamlit as st
import datetime

def fx_rates(cur_from, cur_to, freq = "A", start_year = "2015"):


    if cur_from == "EUR":
        request_ecb = sdmx.Request("ECB")
        fx_rates = (
            request_ecb.data(resource_id="EXR", key={'CURRENCY': cur_to, "FREQ": freq, "EXR_SUFFIX": "A"}, params = {'startPeriod': start_year})
            .to_pandas()
            .reset_index()
            .loc[:, ["CURRENCY", "CURRENCY_DENOM", "TIME_PERIOD", "value"]]
            .set_axis(["to", "from", "period", "value"], axis=1)
        )

        if "EUR" not in set(fx_rates["to"]) and "EUR" in cur_to:
            dummy_fx_eur = (
                fx_rates[["period", "from"]]
                .assign(to=lambda x: "EUR")
                .assign(value=lambda x: 1)
            )
            fx_rates = fx_rates.append(dummy_fx_eur, ignore_index=True)

    if cur_from == "USD":
        request_bis = sdmx.Request("BIS")
        fx_rates = (
            request_bis.data(resource_id = "WEBSTATS_XRU_CURRENT_DATAFLOW", key={"FREQ": freq, "CURRENCY": cur_to, "COLLECTION": "A"}, params={"startPeriod": start_year})
            .to_pandas()
            .reset_index()
            .loc[:, ["CURRENCY", "TIME_PERIOD", "value"]]
            .assign(from_name=lambda x: "USD")
            .set_axis(["to", "period", "value" ,"from"], axis=1)
        )

    fx_rates = (
        fx_rates
        .groupby(["period", "from", "to"])
        .mean()
        .reset_index()
    )

    return(fx_rates)

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def fx_app():
    this_year = datetime.datetime.now().year
    list_of_years = [x for x in range(2010, this_year)]

    with st.sidebar:
        st.header("Parameters")
        cur_from = st.selectbox("From currency", ["EUR", "USD"], 0)
        cur_to = st.multiselect("Convert to", ["USD", "GBP", "CHF", "EUR"], ["USD", "GBP", "EUR"])
        freq = st.selectbox("Frequency needed", ["Annually", "Monthly"], 0)
        start_year = st.selectbox("Start year", list_of_years, len(list_of_years)-1)


    freq_mapp = {
        "Annually":"A",
        "Monthly":"M"
    }

    st.markdown(
        """
        # Currency converter
        
        """)

    fx_rates_df = fx_rates(cur_from, cur_to, freq_mapp[freq], start_year)
    st.write(fx_rates_df)

    with st.sidebar:
        tmp_download_link = download_link(fx_rates_df, 'exchange_rates.csv', 'Click here to download the table!')
        st.markdown(tmp_download_link, unsafe_allow_html=True)

if __name__=="__main__":
    fx_app()