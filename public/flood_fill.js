
onmessage = function (e) {
    //console.log('Message received from main script', e.data[5])
    var workerResult = floodFill(e.data[0], e.data[1], e.data[2], e.data[3], e.data[4], e.data[5], e.data[6])
}



function floodFill(imageData, canvasWidth, canvasHeight, X, Y, fillColour, mode){
    //console.log("image data: ", imageData)
    var startPos = (Y*canvasWidth + X) * 4
    var targetColour = [imageData.data[startPos], imageData.data[startPos+1], imageData.data[startPos+2], imageData.data[startPos+3]]
    if (mode == "Picker"){
        postMessage(["Picked", targetColour])
        return targetColour
    }
    //console.log(targetColour)
    var pixelStack = [[X,Y]]  
    if (matchStartColor(startPos, imageData, [0,0,0, 255]) || matchStartColor(startPos, imageData, fillColour)){
        console.log("cancelled")
        return 0
    }
    while (pixelStack.length > 0){
        var newPos, x, y, pixelPos, reachLeft, reachRight;
        newPos = pixelStack.pop();
        x = newPos[0];
        y = newPos[1];
        
        pixelPos = (y*canvasWidth + x) * 4;
        while(y-- >= 0 && matchStartColor(pixelPos, imageData, targetColour))
        {
            pixelPos -= canvasWidth * 4;
        }
        pixelPos += canvasWidth * 4;
        ++y;
        reachLeft = false;
        reachRight = false;
        while(y++ < canvasHeight-1 && matchStartColor(pixelPos, imageData, targetColour))
        {
            colorPixel(pixelPos, imageData, fillColour);

            if(x > 0)
            {
            if(matchStartColor(pixelPos - 4, imageData, targetColour))
            {
                if(!reachLeft){
                pixelStack.push([x - 1, y]);
                reachLeft = true;
                }
            }
            else if(reachLeft)
            {
                reachLeft = false;
            }
            }
            
            if(x < canvasWidth-1)
            {
            if(matchStartColor(pixelPos + 4, imageData, targetColour))
            {
                if(!reachRight)
                {
                pixelStack.push([x + 1, y]);
                reachRight = true;
                }
            }
            else if(reachRight)
            {
                reachRight = false;
            }
            }
                    
            pixelPos += canvasWidth * 4;
        }
    }
    //console.log(imageData)
    if (mode == "Undo"){
        postMessage(["Undo", imageData, [X,Y, targetColour]] )
    }
    else{
        postMessage(["Fill", imageData, [X,Y, targetColour]] )
    }
    
}
    

function matchStartColor(pixelPos, imageData, targetColour)
{
    var r = imageData.data[pixelPos]	
    var g = imageData.data[pixelPos+1]	
    var b = imageData.data[pixelPos+2]
    var a = imageData.data[pixelPos+3]
    //console.log(r,g,b, targetColour)
    return (r == targetColour[0] && g == targetColour[1] && b == targetColour[2] && a == targetColour[3] ); // && a == targetColour[3]
}
function colorPixel(pixelPos, imageData, fillColour)
{
    imageData.data[pixelPos] = fillColour[0]
    imageData.data[pixelPos+1] = fillColour[1]
    imageData.data[pixelPos+2] = fillColour[2]
    imageData.data[pixelPos+3] = fillColour[3]
}