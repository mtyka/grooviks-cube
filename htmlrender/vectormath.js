//-----------------------------------------------------------------------------             
// Standard 4D vector math utility methods
// When using 4D vectors, positions are represented by [ x, y, z, 1 ]
// and directions are represented by [ x, y, z, 0 ]
//-----------------------------------------------------------------------------             
function vec4() 
{
    this.v = [ 0, 0, 0, 1 ]
}

function vectorSubtract( a, b )
{
    var r = new vec4;
    r.v[0] = a.v[0] - b.v[0];
    r.v[1] = a.v[1] - b.v[1];
    r.v[2] = a.v[2] - b.v[2];
    r.v[3] = a.v[3] - b.v[3];  
    return r;          
}

function vectorAdd( a, b )
{
    var r = new vec4;
    r.v[0] = a.v[0] + b.v[0];
    r.v[1] = a.v[1] + b.v[1];
    r.v[2] = a.v[2] + b.v[2];
    r.v[3] = a.v[3] + b.v[3];  
    return r;          
}

function vectorMultiplyScalar( a, t )
{
    var r = new vec4;
    r.v[0] = a.v[0] * t;
    r.v[1] = a.v[1] * t;
    r.v[2] = a.v[2] * t;
    r.v[3] = a.v[3] * t;  
    return r;          
}

// When t = 0, returns a. When t == 1, returns b.
function vectorLerp( a, b, t )
{
    var d = vectorSubtract( b, a );
    var d1 = vectorMultiplyScalar( d, t );
    return vectorAdd( a, d1 );
}

// returns a + b * t (t is scalar)
function vectorMultiplyAdd( a, b, t )
{
    var d = vectorMultiplyScalar( b, t );
    return vectorAdd( a, d );
}

// returns a + b * t1 + c * t2 (t1,t2 is scalar)
function vectorMultiplyAdd2( a, b, t1, c, t2 )
{
    var d1 = vectorMultiplyScalar( b, t1 );
    var d2 = vectorMultiplyScalar( c, t2 );
    var s = vectorAdd( d1, d2 );
    return vectorAdd( a, s );
}

function vectorSet( v, x, y, z, w )
{
    v.v[0] = x;
    v.v[1] = y;
    v.v[2] = z;
    v.v[3] = w;
}

function vectorCopy( v )
{
    var r = new vec4;
    r.v[0] = v.v[0];
    r.v[1] = v.v[1];
    r.v[2] = v.v[2];
    r.v[3] = v.v[3];
    return r;
}

function vectorNormalize( v )
{
    var mag = v.v[0] * v.v[0] + v.v[1] * v.v[1] + v.v[2] * v.v[2] + v.v[3] * v.v[3];
    if ( mag == 0.0 )
    {
        mag = 1.0
    }
    var r = new vec4;
    mag = Math.sqrt( 1.0 / mag );
    r.v[0] = v.v[0] * mag;
    r.v[1] = v.v[1] * mag;
    r.v[2] = v.v[2] * mag;
    r.v[3] = v.v[3] * mag;
    return r;
}

function vectorCross( a, b )
{
    var r = new vec4;
    r.v[0] = a.v[1]*b.v[2] - a.v[2]*b.v[1];
    r.v[1] = a.v[2]*b.v[0] - a.v[0]*b.v[2];
    r.v[2] = a.v[0]*b.v[1] - a.v[1]*b.v[0];
    r.v[3] = 0.0;
    return r;
}


//-----------------------------------------------------------------------------             
// Note that we're doing column-major matrices. 
// Vectors are pre-multiplied by matrices to transform them, i.e. vtransform = mat * v;
// This is *not* the method OpenGL uses (they post-multiply vectors by matrices)
// If you're not familiar w/ matrices, the upper 3x3 represents a rotation
// and the 3rd column represents the translational component for a 
// orthonormal matrix.
//-----------------------------------------------------------------------------             
function matrix() 
{
    this.m = [ [ 1, 0, 0, 0 ], [ 0, 1, 0, 0 ], [ 0, 0, 1, 0 ], [ 0, 0, 0, 1 ] ];
}

function multiplyMatrix( a, b ) 
{
    var r = new matrix()
    r.m[0][0] = a.m[0][0] * b.m[0][0] + a.m[0][1] * b.m[1][0] + a.m[0][2] * b.m[2][0] + a.m[0][3] * b.m[3][0];
    r.m[0][1] = a.m[0][0] * b.m[0][1] + a.m[0][1] * b.m[1][1] + a.m[0][2] * b.m[2][1] + a.m[0][3] * b.m[3][1];
    r.m[0][2] = a.m[0][0] * b.m[0][2] + a.m[0][1] * b.m[1][2] + a.m[0][2] * b.m[2][2] + a.m[0][3] * b.m[3][2];
    r.m[0][3] = a.m[0][0] * b.m[0][3] + a.m[0][1] * b.m[1][3] + a.m[0][2] * b.m[2][3] + a.m[0][3] * b.m[3][3];

    r.m[1][0] = a.m[1][0] * b.m[0][0] + a.m[1][1] * b.m[1][0] + a.m[1][2] * b.m[2][0] + a.m[1][3] * b.m[3][0];
    r.m[1][1] = a.m[1][0] * b.m[0][1] + a.m[1][1] * b.m[1][1] + a.m[1][2] * b.m[2][1] + a.m[1][3] * b.m[3][1];
    r.m[1][2] = a.m[1][0] * b.m[0][2] + a.m[1][1] * b.m[1][2] + a.m[1][2] * b.m[2][2] + a.m[1][3] * b.m[3][2];
    r.m[1][3] = a.m[1][0] * b.m[0][3] + a.m[1][1] * b.m[1][3] + a.m[1][2] * b.m[2][3] + a.m[1][3] * b.m[3][3];

    r.m[2][0] = a.m[2][0] * b.m[0][0] + a.m[2][1] * b.m[1][0] + a.m[2][2] * b.m[2][0] + a.m[2][3] * b.m[3][0];
    r.m[2][1] = a.m[2][0] * b.m[0][1] + a.m[2][1] * b.m[1][1] + a.m[2][2] * b.m[2][1] + a.m[2][3] * b.m[3][1];
    r.m[2][2] = a.m[2][0] * b.m[0][2] + a.m[2][1] * b.m[1][2] + a.m[2][2] * b.m[2][2] + a.m[2][3] * b.m[3][2];
    r.m[2][3] = a.m[2][0] * b.m[0][3] + a.m[2][1] * b.m[1][3] + a.m[2][2] * b.m[2][3] + a.m[2][3] * b.m[3][3];

    r.m[3][0] = a.m[3][0] * b.m[0][0] + a.m[3][1] * b.m[1][0] + a.m[3][2] * b.m[2][0] + a.m[3][3] * b.m[3][0];
    r.m[3][1] = a.m[3][0] * b.m[0][1] + a.m[3][1] * b.m[1][1] + a.m[3][2] * b.m[2][1] + a.m[3][3] * b.m[3][1];
    r.m[3][2] = a.m[3][0] * b.m[0][2] + a.m[3][1] * b.m[1][2] + a.m[3][2] * b.m[2][2] + a.m[3][3] * b.m[3][2];
    r.m[3][3] = a.m[3][0] * b.m[0][3] + a.m[3][1] * b.m[1][3] + a.m[3][2] * b.m[2][3] + a.m[3][3] * b.m[3][3];
    return r;
}
                  
function vectorMultiply( m, v )
{
    var res = new vec4( );
    res.v[0] = m.m[0][0] * v.v[0] + m.m[0][1] * v.v[1] + m.m[0][2] * v.v[2] + m.m[0][3] * v.v[3];
    res.v[1] = m.m[1][0] * v.v[0] + m.m[1][1] * v.v[1] + m.m[1][2] * v.v[2] + m.m[1][3] * v.v[3];
    res.v[2] = m.m[2][0] * v.v[0] + m.m[2][1] * v.v[1] + m.m[2][2] * v.v[2] + m.m[2][3] * v.v[3];
    res.v[3] = m.m[3][0] * v.v[0] + m.m[3][1] * v.v[1] + m.m[3][2] * v.v[2] + m.m[3][3] * v.v[3];
    return res;
}

function vectorMultiplyProjective( m, v )
{
    // When doing a projective transformation, you end up with a w that is not 1
    // To turn it into a normal position vector, you must divide by w
    // which actually has the effect of doing the projection onto a plane where w = 1
    var r = new vec4( );
    r.v[0] = m.m[0][0] * v.v[0] + m.m[0][1] * v.v[1] + m.m[0][2] * v.v[2] + m.m[0][3] * v.v[3];
    r.v[1] = m.m[1][0] * v.v[0] + m.m[1][1] * v.v[1] + m.m[1][2] * v.v[2] + m.m[1][3] * v.v[3];
    r.v[2] = m.m[2][0] * v.v[0] + m.m[2][1] * v.v[1] + m.m[2][2] * v.v[2] + m.m[2][3] * v.v[3];
    r.v[3] = m.m[3][0] * v.v[0] + m.m[3][1] * v.v[1] + m.m[3][2] * v.v[2] + m.m[3][3] * v.v[3];     
    if ( r.v[3] != 0.0 ) 
    {
        oow = 1.0 / r.v[3];
        r.v[0] = r.v[0] * oow
        r.v[1] = r.v[1] * oow
        r.v[2] = r.v[2] * oow
    }
    r.v[3] = 1.0
    return r;
}


function matrixInvert( src )
{
    // NOTE: This only works for orthonormal matrices
    var r = new matrix()

    // Transpose the upper 3x3.
    r.m[0][0] = src.m[0][0];  r.m[0][1] = src.m[1][0]; r.m[0][2] = src.m[2][0];
    r.m[1][0] = src.m[0][1];  r.m[1][1] = src.m[1][1]; r.m[1][2] = src.m[2][1];
    r.m[2][0] = src.m[0][2];  r.m[2][1] = src.m[1][2]; r.m[2][2] = src.m[2][2];

    // Transform the translation.
    var vTrans = new vec4();
    vectorSet( vTrans, -src.m[0][3], -src.m[1][3], -src.m[2][3], 1.0 );
    var vNewTrans = vectorMultiply( r, vTrans );
    r.m[0][3] = vNewTrans.v[0];
    r.m[1][3] = vNewTrans.v[1];
    r.m[2][3] = vNewTrans.v[2]; 
    return r;
}



