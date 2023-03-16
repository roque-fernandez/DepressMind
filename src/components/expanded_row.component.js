import React from "react";

export default class ExpandedRow extends React.Component {
    render() {
        const { sentence, prevContext, link, folContext, points } = this.props.data;

        console.log("Expanded row sentence: ",sentence, " ", points, " points")

        let color;
        switch (points) {
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
    
        console.log("Data: ",this.props.data);
        return (
            <div>
                <div style={{marginTop: '1em'}}>
                    <p>
                    {prevContext && <span>{prevContext} </span>}
                    <span style={{ color: color }}>{sentence} </span>
                    {folContext && <span>{folContext}</span>}                    
                    </p>
                </div>  
                
                <div><a href={link} target="_blank" rel="noopener noreferrer">See post in Reddit</a></div>

            </div>
        );
    }
}
