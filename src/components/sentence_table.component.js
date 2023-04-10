import React from "react";
import DataTable, { createTheme } from "react-data-table-component";
import ExpandedRow from "./expanded_row.component";
//ICONS
import sadness from "../iconos/sadness.png";
import pessimism from "../iconos/pessimism.png";
import pastFailure from "../iconos/past_failure.png";
import lossPleasure from "../iconos/loss_pleasure.png";
import guiltyFeelings from "../iconos/guilty_feelings.png";
import punishment from "../iconos/punishment_feelings.png";
import selfDislike from "../iconos/self_dislike.png";
import selfCriticalness from "../iconos/self_criticalness.png";
import suicidalThoughts from "../iconos/suicidal_thoughts.png";
import crying from "../iconos/crying.png";
import agitation from "../iconos/agitation.png";
import lossInterest from "../iconos/loss_interest.png";
import indecisiveness from "../iconos/indecisiveness.png";
import worthlessness from "../iconos/worthlessness.png";
import lossEnergy from "../iconos/loss_energy.png";
import sleepingPattern from "../iconos/sleeping_pattern.png";
import irritability from "../iconos/irritability.png";
import appetite from "../iconos/appetite.png";
import concentrationDifficulty from "../iconos/concentration_difficulty.png";
import fatigue from "../iconos/fatigue.png";
import interestSex from "../iconos/interest_sex.png";



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

        console.log(
        "Sentences in table ",
        this.props.title,
        ": ",
        this.props.data,
        " puntos->",
        this.props.points
        );

        // get all sentences together we begin with the sentences with higher points
        this.augmentedData = [];
        this.props.data.forEach((childList, index) => {
            childList.forEach((obj) => {
                obj.points = index + 1; // Add a points field with the corresponding index value (1, 2, or 3)
                this.augmentedData.push(obj);
            });
        });
        this.augmentedData.sort((a, b) => b.points - a.points); // Sort the augmented data in descending order by points

        this.state = {
            numRowsToShow: 10, // Set the initial number of rows to show
        };

        this.icons = [sadness,pessimism,pastFailure,lossPleasure,guiltyFeelings,punishment,selfDislike,selfCriticalness,suicidalThoughts,crying,agitation,lossInterest,indecisiveness,worthlessness,lossEnergy,sleepingPattern,irritability,appetite,concentrationDifficulty,fatigue,interestSex];

        this.columns = [
        {
            name: <span><img src={this.icons[this.props.index]} alt="icon" width="43em" height="43em" style={{marginRight: '1em'}} /><span style={{ fontSize: "x-large", paddingLeft: "10 em" }}>{this.props.title}</span></span>,
            selector: (row) => row.sentence,
            sortable: true,
            icon: <img src={punishment} alt="icon" />,
            cell: (row) => {
                let color;
                switch (row.points) {
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

        
    }

    handleRowClick = (row) => {
        const data = [...this.state.data];
        data[row] = {
        ...data[row],
        showDetails: true,
        };
        this.setState({ data });
    };

    handleShowMoreClick = () => {
        this.setState((prevState) => ({
            numRowsToShow: prevState.numRowsToShow + 10, // Show 10 more rows when the user clicks the button
        }));
    };

    handleShowLessClick = () => {
        this.setState((prevState) => ({
            numRowsToShow: prevState.numRowsToShow - 10, // Show 10 fewer rows when the user clicks the button
        }));
    };

    render() {
        const { numRowsToShow } = this.state;
        const dataToShow = this.augmentedData.slice(0, numRowsToShow);

        const showMoreDisabled = numRowsToShow >= this.augmentedData.length;
        const showLessDisabled = numRowsToShow <= 10;
      
        return (
          <>
            <DataTable
              columns={this.columns}
              data={dataToShow}
              expandableRows
              expandableRowsComponent={ExpandedRow}
              expandableRowExpanded={(row) =>
                row.showDetails ? <ExpandedRow data={row} /> : null
              }
              onRowClicked={this.handleRowClick}
              theme="customTheme"
            />
            <div className="d-flex justify-content-between" style={{marginTop: '1em', marginBottom: '2em'}}>
                <button
                    onClick={this.handleShowLessClick}
                    className="btn btn-light text-center"
                    disabled={showLessDisabled}
                    >
                    Show Less
                </button>
                <button
                    onClick={this.handleShowMoreClick}
                    className="btn btn-light text-center"
                    disabled={showMoreDisabled}
                    >
                    Show More
                </button>
                
            </div>
            
          </>
        );
    }
}