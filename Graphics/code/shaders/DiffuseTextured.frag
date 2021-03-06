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

// Textures
uniform sampler2D diffuseTexture;

out vec4 fragmentColor;

void main()
{
    // Load base values from textures
    vec3 baseDiffuse = texture(diffuseTexture, v2f_texCoord).xyz;

    // Ambient lighting
    vec3 ambientLight = ambientStrength * ambientColor;

    // Diffuse lighting
    vec3 viewSpaceDirToLight = normalize(sunPosition - v2f_viewSpacePosition);
    vec3 viewSpaceNormal = normalize(v2f_viewSpaceNormal);
    float incomingIntensity = max(0.0, dot(viewSpaceNormal, viewSpaceDirToLight));
    vec3 incomingLight = incomingIntensity * sunColor;

    vec3 outgoingLight = (incomingLight + ambientLight) * baseDiffuse;
    fragmentColor = vec4(outgoingLight, 1.0);
}