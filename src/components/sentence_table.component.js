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

class SentenceTable extends React.Component {
  constructor(props) {
    super(props);

    this.columns = [
        {
            name: "Sentence",
            selector: row => row.sentence,
            sortable: true,
            cell: row => <div>{row.sentence}</div>,
        }
    ];

    this.state = {
      data: [
        {
          sentence: "This is the first sentence.",
          previousSentence: "There was nothing before this.",
          link: "https://example.com",
          nextSentence: "This is the second sentence.",
          showDetails: false
        },
        {
          sentence: "This is the second sentence.",
          previousSentence: "This is the first sentence.",
          link: "https://example.com",
          nextSentence: "This is the third sentence.",
          showDetails: false
        },
        {
          sentence: "This is the third sentence.",
          previousSentence: "This is the second sentence.",
          link: "https://example.com",
          nextSentence: "There is nothing after this.",
          showDetails: false
        },
      ],
    };
  }

  handleRowClick = row => {
    const data = [...this.state.data];
    data[row] = {
      ...data[row],
      showDetails: !data[row].showDetails
    };
    this.setState({ data });
  };

  render() {
    return (
      <DataTable
        title="Sentence Table"
        columns={this.columns}
        data={this.state.data}
        expandableRows
        expandableRowsComponent={<ExpandedRow />}
        onRowClicked={this.handleRowClick}
        theme="customTheme"
      />
    );
  }
}

class ExpandedRow extends React.Component {
  render() {
    const { previousSentence, link, nextSentence } = this.props.data;
    return (
      <div>
        <div>Previous Sentence: {previousSentence}</div>
        <div>Link: {link}</div>
        <div>Next Sentence: {nextSentence}</div>
      </div>
    );
  }
}

export default SentenceTable;


