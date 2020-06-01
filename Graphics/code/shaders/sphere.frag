#version 330

// Passed in from vertex shader
in VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec3 v2f_viewSpacePosition;
	vec2 v2f_texCoord;
};

// Lighting information
uniform vec3 sunPosition;
uniform vec3 sunColor;
uniform vec3 ambientColor;
uniform float ambientStrength;

float specular_exponent = 32;

out vec4 fragmentColor;

void main()
{
    // Base color -> load from texture (eventually)
    vec3 baseDiffuse = vec3(0.9, 0.9, 0.9);
    vec3 baseSpecular = vec3(1.0, 1.0, 1.0);

    // Ambient lighting
    vec3 ambientLight = ambientStrength * ambientColor;

    // Diffuse lighting
    vec3 viewSpaceDirToLight = normalize(sunPosition - v2f_viewSpacePosition);
    vec3 viewSpaceNormal = normalize(v2f_viewSpaceNormal);
    float incomingIntensity = max(0.0, dot(viewSpaceNormal, viewSpaceDirToLight));
    vec3 incomingLight = incomingIntensity * sunColor;

    // Specular lighting
    vec3 viewSpaceDirToEye = normalize(-v2f_viewSpacePosition);
    vec3 halfVector = normalize(viewSpaceDirToEye + viewSpaceDirToLight);
    float specularIntensity = max(0.0, dot(halfVector, viewSpaceNormal));
    specularIntensity = pow(specularIntensity, specular_exponent);

    vec3 outgoingLight = (incomingLight + ambientLight) * baseDiffuse;
    outgoingLight = outgoingLight + (incomingLight * specularIntensity * baseSpecular);
    fragmentColor = vec4(outgoingLight, 1.0);
}