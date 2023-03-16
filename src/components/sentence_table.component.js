import React from "react";
import DataTable, { createTheme } from "react-data-table-component";
import  ExpandedRow from "./expanded_row.component";

createTheme("customTheme", {
    text: {
        primary: "#333",
        secondary: "#999",
    },
    background: {
        default: "#fff",
    },
});

export default class SentenceTable extends React.Component {
    constructor(props) {
        super(props);

        console.log("Sentences in table ", this.props.title, ": ", this.props.data)

        this.columns = [
            {
            // name: "Sentence",
            selector: (row) => row.sentence,
            sortable: true,
            cell: (row) => <div>{row.sentence}</div>,
            },
        ];

        this.state = {
            data: [
                {
                sentence: "This is the first sentence",
                previousContext: "There was nothing before this",
                link: "https://example.com",
                folContext: "This is the second sentence",
                showDetails: false,
                },
                {
                sentence: "This is the second sentence",
                previousContext: "This is the first sentence",
                link: "https://example.com",
                folContext: "This is the third sentence",
                showDetails: false,
                },
                {
                sentence: "This is the third sentence",
                previousContext: "This is the second sentence",
                link: "https://example.com",
                folContext: "There is nothing after this",
                showDetails: false,
                },
            ],
        };
    }

    handleRowClick = (row) => {
        const data = [...this.state.data];
        data[row] = {
        ...data[row],
        showDetails: true,
        };
        this.setState({ data });
    };

    render() {
        return (
            <DataTable
            title={this.props.title + " - " + this.props.points + " points"}
            columns={this.columns}
            data={this.props.data}
            expandableRows
            expandableRowsComponent={ExpandedRow} // <--- change here
            expandableRowExpanded={(row) =>
                row.showDetails ? <ExpandedRow data={row} /> : null
            }
            onRowClicked={this.handleRowClick}
            theme="customTheme"
        />
        );
    }
}
