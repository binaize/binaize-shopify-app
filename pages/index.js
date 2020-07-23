import React from "react";

class Conversion extends React.Component {

    componentDidMount() {

        console.log(window.location.search)
        const access_token = new URLSearchParams(window.location.search)
        window.location.href = "https://dev.app.binaize.com/experiment?access_token=" + access_token.get("at");
        // window.location.href = "localhost:3001?access_token=" + access_token.get("at");

    }

    render() {
        return (
            <div>
                <p>Loading...</p>
            </div>
        )
    }

}

export default Conversion;