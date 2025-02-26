from IPython.display import display, HTML


def display_user_paths(paths: dict):
    """
    Display a dictionary of paths in a user-friendly table format in IPython.

    Parameters
    ----------
    paths : dict
        Dictionary where keys are names and values are paths to display.
    """
    # Generate an HTML table with centered text, adaptive styling, and a limited width
    html_content = """
    <style>
        :root {
            --bg-color-light: #ffffff;
            --bg-color-dark: #1e1e1e;
            --text-color-light: #000000;
            --text-color-dark: #ffffff;
            --row-color-light: #f9f9f9;
            --row-color-dark: #333333;
            --header-bg-light: #4CAF50;
            --header-bg-dark: #3e8e41;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: var(--bg-color-dark);
                --text-color: var(--text-color-dark);
                --row-color: var(--row-color-dark);
                --header-bg: var(--header-bg-dark);
            }
        }

        @media (prefers-color-scheme: light) {
            :root {
                --bg-color: var(--bg-color-light);
                --text-color: var(--text-color-light);
                --row-color: var(--row-color-light);
                --header-bg: var(--header-bg-light);
            }
        }

        table {
            border-collapse: collapse;
            width: 80%; /* Reasonable width for the table */
            margin: 20px auto; /* Center the table horizontally */
            text-align: center; /* Center-align the text */
            font-family: Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            border: 1px solid #ddd;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Add a slight shadow for better focus */
        }

        th, td {
            padding: 10px;
            border: 1px solid #ddd;
        }

        thead tr {
            background-color: var(--header-bg);
            color: var(--text-color);
        }

        tbody tr:nth-child(even) {
            background-color: var(--row-color);
        }
    </style>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Path</th>
            </tr>
        </thead>
        <tbody>
    """
    for name, path in paths.items():
        html_content += f"""
        <tr>
            <td>{name}</td>
            <td>{path}</td>
        </tr>
        """
    html_content += """
        </tbody>
    </table>
    """
    display(HTML(html_content))
