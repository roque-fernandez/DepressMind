import React from "react";

export default class ExpandedRow extends React.Component {
    render() {
        const { sentence, previousContext, link, folContext } = this.props.data;
    
        console.log("Data: ",this.props.data);
        return (
            <div>
                <div style={{marginTop: '1em'}}>
                    <p>
                        {previousContext}. <span style={{ color: "red" }}> {sentence}. </span> {folContext}.                        
                    </p>
                </div>  
                
                <div><a href={link} target="_blank" rel="noopener noreferrer">See post in Reddit</a></div>

            </div>
        );
    }
}
