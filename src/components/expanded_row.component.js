import React from "react";

export default class ExpandedRow extends React.Component {
    render() {
        const { sentence, prevContext, link, folContext } = this.props.data;
    
        console.log("Data: ",this.props.data);
        return (
            <div>
                <div style={{marginTop: '1em'}}>
                    <p>
                    {prevContext && <span>{prevContext} </span>}
                    <span style={{ color: "red" }}>{sentence} </span>
                    {folContext && <span>{folContext}</span>}                    
                    </p>
                </div>  
                
                <div><a href={link} target="_blank" rel="noopener noreferrer">See post in Reddit</a></div>

            </div>
        );
    }
}
