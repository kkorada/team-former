I'll enhance the program to handle team types (Type 1 and Type 2) with minimum and maximum member requirements for each role in a team type. Here's the improved solution:

```python
import pandas as pd
from collections import defaultdict

class HackathonTeamFormation:
    def __init__(self, excel_file):
        self.df = pd.read_excel(excel_file)
        self.participants = self.df.to_dict('records')
        self.by_role = defaultdict(list)
        for p in self.participants:
            self.by_role[p['role'].lower()].append(p)
    
    def show_participant_stats(self):
        print("\nAvailable Participants by Role:")
        for role, people in self.by_role.items():
            print(f"{role.capitalize()}: {len(people)}")
        print("\nExperience Distribution:")
        print(self.df['experience'].value_counts())
        print("\nEvaluation Score Stats:")
        print(self.df['evaluation score'].describe())
    
    def form_teams(self, team_types):
        """
        Form teams based on team types with min/max requirements
        
        Args:
            team_types: Dict of team type configurations
            Example:
            {
                'type1': {
                    'min_members': 4,
                    'max_members': 5,
                    'roles': {
                        'Full Stack': {'min': 2, 'max': 3},
                        'Tester': {'min': 1, 'max': 1},
                        'AI Engineer': {'min': 1, 'max': 1}
                    }
                },
                'type2': {
                    'min_members': 3,
                    'max_members': 4,
                    'roles': {
                        'Full Stack': {'min': 1, 'max': 2},
                        'Tester': {'min': 1, 'max': 1},
                        'AI Engineer': {'min': 1, 'max': 1}
                    }
                }
            }
        """
        teams = []
        remaining_participants = self.participants.copy()
        
        # Sort participants by score (best first)
        remaining_participants.sort(key=lambda x: x['evaluation score'], reverse=True)
        
        # First pass: try to form complete teams meeting minimum requirements
        team_type_order = list(team_types.keys())
        team_idx = 0
        
        while True:
            team_type = team_type_order[team_idx % len(team_type_order)]
            type_config = team_types[team_type]
            team = {'type': team_type, 'members': []}
            formed = True
            
            # Try to fill minimum requirements for each role
            for role, req in type_config['roles'].items():
                role_lower = role.lower()
                available = [p for p in remaining_participants if p['role'].lower() == role_lower]
                needed = req['min']
                
                if len(available) < needed:
                    formed = False
                    break
                
                # Take top performers
                selected = available[:needed]
                team['members'].extend(selected)
                for p in selected:
                    remaining_participants.remove(p)
            
            if not formed:
                break
            
            # Try to add more members up to max limits
            for role, req in type_config['roles'].items():
                role_lower = role.lower()
                current = sum(1 for m in team['members'] if m['role'].lower() == role_lower)
                can_add = req['max'] - current
                
                if can_add > 0:
                    available = [p for p in remaining_participants if p['role'].lower() == role_lower]
                    to_add = min(can_add, len(available))
                    
                    if to_add > 0:
                        selected = available[:to_add]
                        team['members'].extend(selected)
                        for p in selected:
                            remaining_participants.remove(p)
            
            # Ensure total team size is within limits
            current_size = len(team['members'])
            if current_size < type_config['min_members']:
                # Try to add any remaining participants to meet min team size
                needed = type_config['min_members'] - current_size
                to_add = min(needed, len(remaining_participants))
                
                if to_add > 0:
                    selected = remaining_participants[:to_add]
                    team['members'].extend(selected)
                    for p in selected:
                        remaining_participants.remove(p)
            
            if len(team['members']) >= type_config['min_members']:
                teams.append(team)
                team_idx += 1
            else:
                # Return members to pool if team couldn't be formed
                for p in team['members']:
                    remaining_participants.append(p)
                break
        
        # Second pass: distribute remaining participants to existing teams
        if remaining_participants:
            print(f"\nDistributing {len(remaining_participants)} remaining participants...")
            remaining_participants.sort(key=lambda x: x['evaluation score'], reverse=True)
            
            for p in remaining_participants:
                best_team_idx = None
                best_score_diff = float('-inf')
                p_role = p['role'].lower()
                
                # Find team that can accept this participant and would benefit most
                for i, team in enumerate(teams):
                    type_config = team_types[team['type']]
                    current_size = len(team['members'])
                    
                    # Check if team can accept more members
                    if current_size >= type_config['max_members']:
                        continue
                    
                    # Check role limits
                    role_count = sum(1 for m in team['members'] if m['role'].lower() == p_role)
                    role_max = type_config['roles'].get(role.title(), {}).get('max', 0)
                    
                    if role_max > 0 and role_count >= role_max:
                        continue
                    
                    # Calculate how much this would improve the team's average score
                    current_avg = sum(m['evaluation score'] for m in team['members']) / current_size if current_size > 0 else 0
                    new_avg = (sum(m['evaluation score'] for m in team['members']) + p['evaluation score']) / (current_size + 1)
                    score_diff = new_avg - current_avg
                    
                    if score_diff > best_score_diff:
                        best_score_diff = score_diff
                        best_team_idx = i
                
                if best_team_idx is not None:
                    teams[best_team_idx]['members'].append(p)
                    remaining_participants.remove(p)
        
        return teams, remaining_participants
    
    def print_teams(self, teams, team_types):
        """Print the formed teams with their configurations"""
        for i, team in enumerate(teams, 1):
            type_config = team_types[team['type']]
            print(f"\nTeam {i} (Type: {team['type']}, Size: {len(team['members'])}/{type_config['max_members']}):")
            print("-" * 50)
            
            total_score = 0
            role_counts = defaultdict(int)
            
            for member in team['members']:
                print(f"{member['name']} ({member['role']}, Exp: {member['experience']}, Score: {member['evaluation score']})")
                total_score += member['evaluation score']
                role_counts[member['role']] += 1
            
            avg_score = total_score / len(team['members']) if team['members'] else 0
            print("\nRole Distribution:")
            for role, req in type_config['roles'].items():
                current = role_counts.get(role, 0)
                print(f"{role}: {current} (min: {req['min']}, max: {req['max']})")
            
            print(f"\nTotal Score: {total_score:.1f}, Average: {avg_score:.1f}")
            print("-" * 50)
    
    def balance_teams(self, teams, team_types):
        """Balance teams by swapping similar-role members to improve fairness"""
        improved = True
        iterations = 0
        
        while improved and iterations < 100:
            improved = False
            iterations += 1
            
            # Calculate current team metrics
            team_metrics = []
            for team in teams:
                members = team['members']
                if not members:
                    team_metrics.append({'avg_score': 0, 'avg_exp': 0})
                    continue
                
                total_score = sum(m['evaluation score'] for m in members)
                total_exp = sum(m['experience'] for m in members)
                team_metrics.append({
                    'avg_score': total_score / len(members),
                    'avg_exp': total_exp / len(members),
                    'size': len(members)
                })
            
            # Try to find beneficial swaps
            for i in range(len(teams)):
                for j in range(i+1, len(teams)):
                    type_i = teams[i]['type']
                    type_j = teams[j]['type']
                    
                    # Only swap between teams of same type
                    if type_i != type_j:
                        continue
                    
                    # Check if both teams can participate in swaps
                    type_config = team_types[type_i]
                    
                    for m1 in teams[i]['members']:
                        for m2 in teams[j]['members']:
                            if m1['role'] == m2['role']:
                                # Calculate potential new averages
                                new_avg_i_score = (team_metrics[i]['avg_score'] * team_metrics[i]['size'] - m1['evaluation score'] + m2['evaluation score']) / team_metrics[i]['size']
                                new_avg_j_score = (team_metrics[j]['avg_score'] * team_metrics[j]['size'] - m2['evaluation score'] + m1['evaluation score']) / team_metrics[j]['size']
                                
                                # Calculate current and potential imbalances
                                current_imbalance = abs(team_metrics[i]['avg_score'] - team_metrics[j]['avg_score'])
                                new_imbalance = abs(new_avg_i_score - new_avg_j_score)
                                
                                if new_imbalance < current_imbalance:
                                    # Perform the swap
                                    teams[i]['members'].remove(m1)
                                    teams[j]['members'].remove(m2)
                                    teams[i]['members'].append(m2)
                                    teams[j]['members'].append(m1)
                                    improved = True
                                    break
                        
                        if improved:
                            break
                    if improved:
                        break
                if improved:
                    break
        
        return teams

# Example usage
if __name__ == "__main__":
    # Initialize with your Excel file
    team_former = HackathonTeamFormation("hackathon_participants.xlsx")
    
    # Show participant statistics
    team_former.show_participant_stats()
    
    # Define team types with min/max requirements
    team_types = {
        'type1': {
            'min_members': 4,
            'max_members': 5,
            'roles': {
                'Full Stack': {'min': 2, 'max': 3},
                'Tester': {'min': 1, 'max': 1},
                'AI Engineer': {'min': 1, 'max': 1}
            }
        },
        'type2': {
            'min_members': 3,
            'max_members': 4,
            'roles': {
                'Full Stack': {'min': 1, 'max': 2},
                'Tester': {'min': 1, 'max': 1},
                'AI Engineer': {'min': 1, 'max': 1}
            }
        }
    }
    
    # Form teams
    teams, remaining = team_former.form_teams(team_types)
    
    # Balance teams
    balanced_teams = team_former.balance_teams(teams, team_types)
    
    # Print the teams
    print("\nFinal Teams:")
    team_former.print_teams(balanced_teams, team_types)
    
    # Print remaining participants
    if remaining:
        print("\nRemaining Participants:")
        for p in remaining:
            print(f"{p['name']} ({p['role']}, Score: {p['evaluation score']})")
    else:
        print("\nAll participants have been assigned to teams.")
```

## Key Features:

1. **Team Type Configuration**:
   - Define different team types (Type 1, Type 2, etc.)
   - Each type has:
     - Minimum and maximum total team size
     - Role-specific minimum and maximum requirements

2. **Intelligent Team Formation**:
   - First tries to form complete teams meeting minimum requirements
   - Then fills up to maximum limits with best available participants
   - Alternates between team types for balanced distribution

3. **Remaining Participant Distribution**:
   - Distributes leftover participants to teams that:
     - Have capacity (under max size)
     - Won't exceed role limits
     - Will benefit most from the additional member (based on score improvement)

4. **Team Balancing**:
   - Swaps similar-role members between teams of the same type
   - Reduces score disparities between teams
   - Maintains all team composition rules during swaps

5. **Detailed Reporting**:
   - Shows team type and size compliance
   - Displays role distribution vs. requirements
   - Includes team performance metrics

## Usage Instructions:

1. Prepare your Excel file with columns: name, email, phone, role, experience, evaluation score
2. Define your team types in the `team_types` dictionary with:
   - `min_members`: Minimum team size
   - `max_members`: Maximum team size
   - `roles`: Dictionary of role requirements (min/max for each role)
3. The program will:
   - Form teams according to your specifications
   - Distribute remaining participants optimally
   - Balance teams for fairness
   - Provide detailed output showing team compositions

This solution provides maximum flexibility in team configuration while ensuring efficient use of all participants and maintaining balanced teams.
