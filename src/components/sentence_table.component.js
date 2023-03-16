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

        console.log("Sentences in table ", this.props.title, ": ", this.props.data, " puntos->",this.props.points)

        // this.columns = [
        //     {
        //     // name: "Sentence",
        //     selector: (row) => row.sentence,
        //     sortable: true,
        //     cell: (row) => <div>{row.sentence}</div>,
        //     },
        // ];

        this.columns = [
            {
                name: <span style={{ fontSize: "x-large" }}>{this.props.title}</span>,
                selector: (row) => row.sentence,
                sortable: true,
                cell: (row) => {
                    let color;
                    switch (this.props.points) {
                    case 1:
                        color = "rgba(255, 195, 0, 1)";
                        break;
                    case 2:
                        color = "rgba(255, 123, 0, 1)";
                        break;
                    case 3:
                        color = "red";
                        break;
                    default:
                        color = "black";
                        break;
                    }
                    return (
                    <div style={{ color: color }}>
                        {row.sentence}
                    </div>
                    )
                },
            },
        ];

        this.augmentedData = this.props.data.map(obj => {
            return { ...obj, points: this.props.points };
        });

        this.state = {
            
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
                columns={this.columns}
                data={this.augmentedData}
                expandableRows
                expandableRowsComponent={ExpandedRow} // <--- change here
                expandableRowExpanded={(row) =>
                    row.showDetails ? <ExpandedRow data={row}/> : null
            }
            onRowClicked={this.handleRowClick}
            theme="customTheme"
        />
        );
    }
}
