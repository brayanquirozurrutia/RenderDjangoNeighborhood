const getLocation = ()=>{

    const success = (position)=>{
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        document.getElementById('id_latitude').value = latitude;
        document.getElementById('id_longitude').value = longitude;
    }

    const error = ()=>{
        console.log('ERROR')
    }


    navigator.geolocation.getCurrentPosition(success, error);

}

window.addEventListener('load', getLocation);