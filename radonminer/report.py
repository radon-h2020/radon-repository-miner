"""
This module is responsible to generate the HTML report for the mining
"""
import datetime

from typing import List
from radonminer.files import FailureProneFile


def create_report(full_name_or_id:str, labeled_files: List[FailureProneFile]) -> str:
    """
    Generate an HTML report for the crawled repositories.
    :param labeled_files: a list of labeled files
    :return: the HTML report
    """
    now = datetime.datetime.now()
    generation_date = datetime.date(now.year, now.month, now.day)

    table_body = ''
    for i in range(0, len(labeled_files)):
        table_body += """
            <tr>
              <th scope="row">{0}</th>
              <td>{1}</td>
              <td><a href="https://github.com/{2}/blob/{3}/{1}" target="_blank">{3}</a></td>
              <td><a href="https://github.com/{2}/commit/{4}" target="_blank">{4}</a></td>
            </tr>
        """.format(
            i+1,
            labeled_files[i].filepath,
            full_name_or_id,
            labeled_files[i].commit,
            labeled_files[i].fixing_commit
        )

    return """
        <!doctype html>
        <html lang="en">
            <header>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            </header>
            <body class="bg-dark text-white">
                <br/>
                <div class="row text-center">
                    <div class="col text-center">
                        <h2>RepositoryMiner Report</h2>
                        <p class="font-weight-light text-center"><a href="{0}" target="_blank">{1}</a> </p> <!-- Repository -->
                        <p class="font-weight-light text-center">This report was generated on: {2} </p> <!-- Report generation date -->
                    </div>
                </div>
    
                <div class="card align-items-center bg-dark">
                    <br/>
                    <i class="fa fa-bug fa-2x" style="color:#dc3545;"></i>
                    <h2>{3}</h2>  <!-- Number of failure-prone scripts -->
                    <p class="font-weight-light text-center">Failure-prone scripts</p>
                </div>
             
                <br/>
                <table class="table table-striped table-dark">
                    <thead>
                        <tr>
                          <th scope="col">#</th>
                          <th scope="col"><span class="badge badge-pill badge-light">Filepath</span></th>
                          <th scope="col"><span class="badge badge-pill badge-info">Commit</span></th>
                          <th scope="col"><span class="badge badge-pill badge-success">Fixing commit</span></th>
                        </tr>
                    </thead
                    <tbody> 
                    {4}  <!-- Table body -->
                    </tbody> 
                </table>
            </body>
            <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
           
        </html> 
        """.format(
        f'https://github.com/{full_name_or_id}',
        full_name_or_id,
        generation_date,
        len(labeled_files),
        table_body)
