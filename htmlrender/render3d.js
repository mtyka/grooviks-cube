// This library requires vectormath.js.  
// Make sure you include it too
            
//-----------------------------------------------------------------------------             
// Some basics of doing a 3d -> 2d transformation: There are 3 important matrices
// 1) The 'camera' or 'view' matrix: This represents the *inverse* of position
// and orientation of the camera in world space, and is used to transform
// world-space points into the coordinate frame of the camera.
// The camera "looks" down its -z axis, its x axis is pointing right in the image plane
// and its y axis is pointing up in the image plane. All geometry will be projected
// onto the z = -1 plane.
// 2) The 'projection' matrix: This transforms geometry in camera space to
// lie on the z =-1 plane. In projection space, everything that lies
// between -1 and 1 in x, y and z will show up on screen.
// 3) The 'viewport' matrix: This transforms geometry in projection space to
// pixel space on screen by translating and scaling x and y. Z is left unchanged.
//-----------------------------------------------------------------------------             
function buildProjectionMatrix( left, right, bottom, top, near, far )
{
    var r = new matrix();
    r.m[0][0] = ( 2 * near ) / ( right - left );
    r.m[1][1] = ( 2 * near ) / ( top - bottom );
    r.m[2][0] = ( right + left ) / ( right - left );    
    r.m[2][1] = ( top + bottom ) / ( top - bottom );     
    
    r.m[2][3] = -1;
    r.m[3][2] = 2 * far * near / ( far - near );
    return r;
}

//-----------------------------------------------------------------------------             
// The way to think about how to build a view matrix: Start with trying to
// make a transform that transforms from camera space to world space.
// Such a transform should have the property that post-multiplying the
// matrix by the column vector [ 0 0 0 1 ] should result in the camera origin
// in world space. Post-multiplying the matrix by [ 0 0 1 0 ] should result
// in the 'z' axis of the camera in world space, etc. The first property means that
// the 3rd column (the translational component of the matrix) needs to be
// the camera location in 3D space (equals 'eye'). The second means that each
// column of the matrix represents the x, y, and z axes of the camera.
// Inverting this matrix results in the view matrix that transforms world-space
// points into camera-space points.
//-----------------------------------------------------------------------------             
function buildViewMatrix( eye, center, up )
{
    var f = vectorSubtract( eye, center );

    f = vectorNormalize( f );
    var s = vectorCross( up, f );
    s = vectorNormalize( s );
    var u = vectorCross( f, s );
    u = vectorNormalize( u );

    var t = new matrix();
    t.m[0][3] = eye.v[0];
    t.m[1][3] = eye.v[1];
    t.m[2][3] = eye.v[2];
  
    var rot = new matrix();
    rot.m[0][0] = s.v[0]; 
    rot.m[0][1] = u.v[0];
    rot.m[0][2] = f.v[0];
    
    rot.m[1][0] = s.v[1]; 
    rot.m[1][1] = u.v[1];
    rot.m[1][2] = f.v[1];
   
    rot.m[2][0] = s.v[2]; 
    rot.m[2][1] = u.v[2];
    rot.m[2][2] = f.v[2];

    var v = multiplyMatrix( t, rot );        
    var vInv = matrixInvert( v );    
    return vInv;
}

function buildViewportTransform( width, height )
{
    var r = new matrix();
    r.m[0][0] = 0.5 * width; 
    r.m[0][3] = 0.5 * height; 
    r.m[1][1] = -0.5 * height; 
    r.m[1][3] = 0.5 * height;
    return r; 
}
                    

//-----------------------------------------------------------------------------
// This draws a quad, projecting it from world space to screenspace, and then rendering it.
// Arguments:
// viewProj: a matrix which concatenates the view + projection matrices
// viewProjViewport: a matrix which concatenates the view, projection, and viewport matrices
// 
//-----------------------------------------------------------------------------             
function drawQuad( ctx, viewProj, viewProjViewport, p1, p2, p3, p4, color ) 
{
    // Backface cull first
    var b1 = vectorMultiplyProjective( viewProj, p1 );
    var b2 = vectorMultiplyProjective( viewProj, p2 );
    var b3 = vectorMultiplyProjective( viewProj, p3 );
    var e1 = vectorSubtract( b2, b1 );
    var e2 = vectorSubtract( b3, b1 );
    var c = vectorCross( e1, e2 );
    if ( c.v[2] <= 0.0 )
    {
        return;
    }
            
    ctx.fillStyle = "rgba(" + 255*color[2] + "," + 255*color[1] + "," + 255*color[0] + ",1)";
    ctx.globalAlpha = 1.0; 
     
    // Transform all points into viewport space
    var vp1 = vectorMultiplyProjective( viewProjViewport, p1 );  
    var vp2 = vectorMultiplyProjective( viewProjViewport, p2 );  
    var vp3 = vectorMultiplyProjective( viewProjViewport, p3 );  
    var vp4 = vectorMultiplyProjective( viewProjViewport, p4 );
        
    // Draw a filled quad  
    ctx.beginPath();   
    ctx.moveTo(vp1.v[0], vp1.v[1]);   
    ctx.lineTo(vp2.v[0], vp2.v[1]);   
    ctx.lineTo(vp3.v[0], vp3.v[1]);   
    ctx.lineTo(vp4.v[0], vp4.v[1]);   
    ctx.closePath();   
    ctx.fill();
}   

