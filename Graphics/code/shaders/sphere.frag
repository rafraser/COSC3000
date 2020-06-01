#version 330

in VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec3 v2f_viewSpacePosition;
	vec2 v2f_texCoord;
};

out vec4 fragmentColor;

float specular_exponent = 1.0;

vec3 fresnelSchick(vec3 r0, float cosAngle)
{
	return r0 + (vec3(1.0) - r0) * pow(1.0 - cosAngle, 5.0);
}

void main() 
{
    vec3 diffuseColor = vec3(1.0, 0.0, 0.0);
    vec3 specularColor = vec3(0.1, 0.0, 0.0);

    vec3 viewSpaceNormal = normalize(v2f_viewSpaceNormal);
    vec3 viewSpaceDirToEye = normalize(-v2f_viewSpacePosition);

    float specularNormalization = ((specular_exponent + 2.0) / (2.0));

    vec3 color = vec3(1.0, 0.0, 0.0);
    fragmentColor = vec4(color, 1.0);
}