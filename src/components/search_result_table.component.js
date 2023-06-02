import React from "react";
import DataTable, { createTheme } from "react-data-table-component";


createTheme("customTheme", {
    text: {
        primary: "#333",
        secondary: "#999",
    },
    background: {
        default: "#fff",
    },
});

export default class PreviewTable extends React.Component {
    constructor(props) {
        super(props);

        console.log("Sentences in table posts", this.props.title, ": ", this.props.data)

        this.columns = [
            {
                name: "Username",
                selector: (row) => row.username,
                sortable: true,
                minWidth: "80px",
                maxWidth: "130px",
                cell: (row) => (
                    <div style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>
                      {row.username}
                    </div>
                ),
              },
              {
                name: "Post",
                selector: (row) => row.text,
                sortable: true,
                minWidth: "370px",
                maxWidth: "none",
                cell: (row) => (
                    <div style={{ whiteSpace: "pre-wrap", wordWrap: "break-word", fontSize: "smaller" }}>
                    {row.text}
                  </div>
                ),
              },
        ];

        this.state = {
            
        }
    }

    

    render() {
        return (
            <DataTable
            columns={this.columns}
            data={this.props.data}
            theme="customTheme"
            />
        );
    }
}
